import os
from dotenv import load_dotenv
import numpy as np
import pydicom
import numpy as np
from pydicom.errors import InvalidDicomError
import logging
from fastapi import File, UploadFile, Depends
from pydicom.dataset import Dataset
from api.py_models.py_models import UploadDICOMResponseModel, UploadResultItem
from db.core.exceptions import *
import shutil, os, uuid, zipfile
import tempfile
from typing import Dict
from src.db.crud.crud_dicom import *
from src.db.database.database import get_db


# Logging-Konfiguration
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/tmp/processed")
UPLOAD_TMP_DIR = os.getenv("UPLOAD_TMP_DIR", "storage/tmp")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(UPLOAD_TMP_DIR, exist_ok=True)

# ===========================================
# DICOM Datei lesen (Metadaten und Bildinfo)
# ===========================================
def extract_metadata(ds: Dataset) -> Dict:
    """
    Liest eine DICOM-Datei und extrahiert DSGVO-konforme Metadaten und Bildinformationen.
    """
    try:
        # # DICOM-Datei einlesen
        # dicom = pydicom.dcmread(file_path)
        
        # DSGVO-konforme Metadaten extrahieren (keine personenbezogenen Daten)
        metadata = {
            "dicom_modality": getattr(ds, "Modality", "N/A"),
            "dicom_sop_class_uid": getattr(ds, "SOPClassUID", "N/A"),
            "dicom_manufacturer": getattr(ds, "Manufacturer", "N/A"),
            "dicom_rows": getattr(ds, "Rows", None),
            "dicom_columns": getattr(ds, "Columns", None),
            "dicom_bits_allocated": getattr(ds, "BitsAllocated", None),
            "dicom_photometric_interpretation": getattr(ds, "PhotometricInterpretation", "N/A"),
            "dicom_transfer_syntax_uid": getattr(ds.file_meta, "TransferSyntaxUID", "N/A"),
            #TODO: filepath holen "dicom_file_path": file_path
        }
        
        # Bilddaten extrahieren
        pixel_array = ds.pixel_array
        image_info = {
            "shape": pixel_array.shape,
            "data_type": str(pixel_array.dtype),
            "min_pixel_value": np.min(pixel_array),
            "max_pixel_value": np.max(pixel_array)
        }
        
        return {
            "status": "success",
            "metadata": metadata,
            "image_info": image_info
        }
    
    # except InvalidDicomError:
    #     return {"status": "error", "message": "Ungültige DICOM-Datei."}
    except Exception as e:
        return {"status": "error", "message": f"Fehler beim Einlesen: {str(e)}"}

def receive_file(file: UploadFile, db: Session):
    """Empfängt eine Datei, prüft Endung (.dcm/.zip),
    speichert sie temporär, 
    übergibt zur Verarbeitung und räumt auf."""

    filename = file.filename.lower()
    if not filename.endswith((".dcm", ".zip")):
        logger.error(f"Invalid file type uploaded: {filename}")
        raise InvalidDICOMFileType(f"Ungültiger Dateityp: '{filename}'. Erlaubt sind nur .dcm oder .zip.")

    tmp_filepath = os.path.join(UPLOAD_TMP_DIR, f"{uuid.uuid4()}.dcm")

    try:
        # Dateiinhalt in temporäre Datei schreiben
        try:
            with open(tmp_filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise DICOMProcessingError(f"Fehler beim Zwischenspeichern der Datei: {str(e)}")

        # Verarbeiten der Datei -> Übergabe an nächste Funktion
        if filename.endswith(".dcm"):
            result = upload_dicom(tmp_filepath, db)
            return UploadDICOMResponseModel(
                message="DICOM-Datei erfolgreich verarbeitet",
                data=[result]
            )
        elif filename.endswith(".zip"):
            result = upload_dicom_zip(tmp_filepath)
            return result

    # Löschen der temporären Datei 
    finally:
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)

def upload_dicom(tmp_filepath:str, db: Session) -> UploadResultItem:
    """Führt den vollständigen Upload-Workflow für eine DICOM-Datei durch:
    - Validierung
    - Extraktion von Pixeldaten und dessen Speicherung in einem Verzeichnis
    - Extraktion der DICOM Metadaten und dessen Speicherung in die Datenbank
    - Rückgabe von Ergebnisdaten (z.B. für API-Response)"""

    ds = load_dicom_file(tmp_filepath)
    validate_dicom(ds)
    #ds = anonymize_dicom(ds) -> Funktion wird erstmal nicht angewendet
    pixel_array = extract_pixel_array(ds)
    #metadata = extract_metadata(ds)
    #Weiterleitung an einer Funktion aus crud_dicom.py
    #store_dicom_metadata(db, metadata["metadata"])
    return store_dicom_and_pixelarray(ds, pixel_array, db)
    
def load_dicom_file(tmp_filepath:str) -> pydicom.Dataset:
    #Schaue nach, ob die Datei DICOM konform ist
    try:
        ds = pydicom.dcmread(tmp_filepath)
        return ds
        #logging.info(f"[Upload] DICOM-Datei erfolgreich gelesen: {file_path}")
    except InvalidDicomError:
        raise InvalidDICOMFileType("Datei ist kein gültiges DICOM-Format.")
    except Exception as e:
        #logging.error(f"[Upload] Allgemeiner Fehler beim Lesen der Datei: {file_path} → {str(e)}")
        raise DICOMProcessingError(f"Unerwarteter Fehler: {str(e)}")
    
def validate_dicom(ds: Dataset) -> None:
    """
    Führt alle notwendigen Validierungen an der DICOM-Datei durch.
    Wirft bei Fehlern Exceptions.
    """

    check_pixeldata(ds)
    check_required_tags(ds)

def check_required_tags(ds: Dataset) -> None:
    """Prüft, ob alle benötigten Tags vorhanden sind."""
    required_tags = {"SOPInstanceUID", "SOPClassUID", "Modality"}
    missing_tags = []

    for tag in required_tags:
        if tag not in ds:
            missing_tags.append(tag)
            continue

    if missing_tags:
        #logging.error(f"[Validation] Fehlende Pflichtfelder (Type 1): {fehlende_typ1}")
        raise MissingRequiredTagError(f"Fehlende Pflichtfelder: {', '.join(missing_tags)}")

def check_pixeldata(ds: Dataset) -> None:
    """Prüft, ob PixelData vorhanden ist."""

    if not hasattr(ds, "PixelData"):
        #logging.error(f"[Validation] Fehlender 'PixelData' in Datei: {filename}")
        raise MissingPixelData("DICOM-File hat keine Pixeldata")

#Aktuell wird diese Funktion nicht verwendet
def anonymize_dicom(ds: pydicom.Dataset) -> pydicom.Dataset:
    """
    Entfernt oder ersetzt sensible Patientendaten im DICOM-Datensatz.
    Gibt einen anonymisierten Datensatz zurück.
    """

    tags_to_anonymize = [
        "PatientName",              # Name des Patienten
        "InstitutionName",          # Name der Klinik
        "ReferringPhysicianName",   # Überweisender Arzt
        "PatientAddress",           # Adresse
        #"PatientID",                # Interne ID
        #"PatientBirthDate",         # Geburtsdatum
        #"OtherPatientIDs",          # Weitere IDs
        #"AccessionNumber",          # Zugriffsnummer
        #"OperatorsName",            # Bedienername
        #"IssuerOfPatientID",        # ID-Aussteller
        #"StudyID"                   # Studiennummer
    ]

    for tag in tags_to_anonymize:
        if tag in ds:
            ds[tag].value = "ANONYMIZED"
        
    return ds

def extract_pixel_array(ds: pydicom.Dataset):
    """
    Wandelt das DICOM-Bild in ein NumPy-Array um und speichert es im .npy-Format.
    """
    try:
        pixel_array = ds.pixel_array.astype(np.float32)
        logging.info(f"[Extractor] Pixel-Array erfolgreich extrahiert")
    except Exception as e:
        logging.error(f"[Extractor] Fehler beim Extrahieren des Pixel-Arrays: {str(e)}")
        raise DICOMExtractionError("Fehler beim Extrahieren des Pixel-Arrays.")
    
    return pixel_array

def store_dicom_and_pixelarray(ds: pydicom.Dataset, pixel_array, db:Session) -> UploadResultItem:
    """Speicherung der DICOM-Datei und die extrahierte Pixelarray."""

    sop_uid = ds.SOPInstanceUID
    anon_path = os.path.join(UPLOAD_DIR, f"{sop_uid}_anon.dcm")
    npy_path = os.path.join(PROCESSED_DIR, f"{sop_uid}_anon.npy")

    # Speichern der DICOM-Datei
    try:
        ds.save_as(anon_path)
        logging.info(f"[Datei] Anonymisierte Datei gespeichert: {anon_path}")
    except Exception as e:
        logging.error(f"[Datei] Fehler beim Speichern der anonymisierten Datei: {anon_path} → {str(e)}")
        raise DICOMProcessingError(f"Fehler beim Speichern der anonymisierten Datei: {str(e)}")

    # Speichern des Pixel-Arrays
    try:
        np.save(npy_path, pixel_array)
        logging.info(f"[PixelData] Pixel-Array gespeichert unter: {npy_path}")
    except Exception as e:
        logging.error(f"[PixelData] Fehler beim Speichern des Pixel-Arrays: {str(e)}")
        raise DICOMProcessingError(f"Fehler beim Speichern des Pixel-Arrays: {str(e)}")
    
    # Extraktion und Speicherung der Metadaten
    metadata_dict = extract_metadata(ds)["metadata"]
    try:
        store_dicom_metadata(db, metadata_dict)
    except Exception as e:
        raise DICOMProcessingError(f"Fehler beim Speichern der Metadaten: {str(e)}")


    return UploadResultItem(
        sop_instance_uid=sop_uid,
        saved_dicom_path=anon_path,
        saved_pixel_array_path=npy_path
    )

def upload_dicom_zip(zip_path: str) -> UploadDICOMResponseModel:
    """Verarbeitet eine ZIP-Datei mit mehreren DICOM-Dateien."""

    results = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
        except Exception as e:
            raise DICOMProcessingError(f"Fehler beim Entpacken der ZIP-Datei: {str(e)}")

        for root, _, files in os.walk(tmp_dir):
            for filename in files:
                if not filename.lower().endswith(".dcm"):
                    logger.warning(f"[ZIP] Ungültige Datei in ZIP übersprungen: {filename}")
                    continue

                dicom_path = os.path.join(root, filename)

                try:
                    result_item = upload_dicom(dicom_path)
                    results.append(result_item)
                except Exception as e:
                    logger.error(f"Fehler bei Datei {filename}: {str(e)}")
                    raise DICOMProcessingError(f"Fehler bei Datei {filename}: {str(e)}")

    return UploadDICOMResponseModel(
        message=f"{len(results)} DICOM-Datei(en) erfolgreich verarbeitet.",
        data=results
    )

def delete_upload_dicom(sop_uid:str) -> None:
    """Löscht die DICOM-Upload Files, also: die .dcm und .npy anhand der SOPInstanceUID"""

    filename_dcm = f"{sop_uid}_anon.dcm"
    filepath_dcm = os.path.join(UPLOAD_DIR, filename_dcm)
    filename_npy = f"{sop_uid}_anon.npy"
    filepath_npy = os.path.join(PROCESSED_DIR, filename_npy)

    if os.path.exists(filepath_dcm) and os.path.exists(filepath_npy):
        os.remove(filepath_dcm)
        os.remove(filepath_npy)
    else:
        raise FileNotFoundError(f"Datei {filepath_dcm} nicht gefunden")
    
def get_all_stored_dicom() -> list:
    """Listet alle DICOM-Bilder, die gerade gespeichert sind."""

    result = []

    for file in os.listdir(UPLOAD_DIR):
        filename = os.path.basename(file)
        result.append(filename)
    return result        
    




