#TODO: Alle Funktionalitäten für den DICOM-Upload (NICHT Datenbank!!) hier in dieser Datei zusammenführen

import os
from dotenv import load_dotenv
import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError
import logging
from fastapi import File, UploadFile
from pydicom.dataset import Dataset
from api.py_models.py_models import UploadDICOMResponseModel, UploadResultItem
from db.core.exceptions import *
import shutil, os, uuid, zipfile
import tempfile


# Logging-Konfiguration
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)





# # DICOM-spezifische Services
# from services.dicom.anonymizer import anonymize_dicom_fields
# from services.dicom.hasher import generate_dicom_hash
# from services.dicom.extractor import extract_pixel_array
# from services.dicom.metadata import extract_metadata
# from services.dicom.validation import run_full_validation

# # Datenbank-Zugriff
# from db.crud import crud_dicom
# from db.database.database import get_db

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/tmp/processed")
UPLOAD_TMP_DIR = os.getenv("UPLOAD_TMP_DIR", "storage/tmp")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(UPLOAD_TMP_DIR, exist_ok=True)

def receive_file(file: UploadFile = File(...)):
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
            result = upload_dicom(tmp_filepath)
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

def upload_dicom(tmp_filepath:str) -> UploadResultItem:
    """Führt den vollständigen Upload-Workflow für eine DICOM-Datei durch:
    - Validierung
    - Anonymisierung
    - Extraktion von Pixeldaten und dessen Speicherung
    - Rückgabe von Ergebnisdaten (z. B. für API-Response)"""

    ds = load_dicom_file(tmp_filepath)
    validate_dicom(ds)
    ds = anonymize_dicom(ds)
    pixel_array = extract_pixel_array(ds)
    #metadata = extract_metadata(ds) -> TODO: eher für Maimuna relevant
    return store_dicom_and_data(ds, pixel_array)
    
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
    #TODO: final entscheiden ob check_modality nötig ist
    #check_modality(ds)

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

        # value = getattr(ds, tag)
        # if tag_typ == 1 and (value is None or str(value).strip() == ""):
        #     fehlende_typ1.append(tag)
        # elif tag_typ == 2 and (value is None or str(value).strip() == ""):
        #     logging.warning(f"[Validation] {tag} ist leer – erlaubt, aber protokolliert.")

def check_pixeldata(ds: Dataset) -> None:
    """Prüft, ob PixelData vorhanden ist."""

    if not hasattr(ds, "PixelData"):
        #logging.error(f"[Validation] Fehlender 'PixelData' in Datei: {filename}")
        raise MissingPixelData("DICOM-File hat keine Pixeldata")

#TODO: final entschieden, was wirklich anonymisiert wird 
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
    # if output_dir is None:
    #     output_dir = os.getenv("PROCESSED_DIR", "/tmp/processed")
    #     logging.info(f"[Extractor] Verwende Standardverzeichnis: {output_dir}")

    # os.makedirs(output_dir, exist_ok=True)

    try:
        pixel_array = ds.pixel_array.astype(np.float32)
        logging.info(f"[Extractor] Pixel-Array erfolgreich extrahiert")
    except Exception as e:
        logging.error(f"[Extractor] Fehler beim Extrahieren des Pixel-Arrays: {str(e)}")
        raise DICOMExtractionError("Fehler beim Extrahieren des Pixel-Arrays.")
    
    return pixel_array

    # out_path = os.path.join(output_dir, f"{hash_name}_anon.npy")
    # np.save(out_path, array)
    # logging.info(f"[Extractor] Pixel-Array gespeichert unter: {out_path}")
    # return out_path

def store_dicom_and_data(ds: pydicom.Dataset, pixel_array) -> UploadResultItem:
    """Speicherung der DICOM-Datei und die extrahierte Pixelarray."""

    #upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    #os.makedirs(upload_dir, exist_ok=True)
    #TO DO: hier statt dicom_hash, die SOPInstanceUID der Datei verwenden
    sop_uid = ds.SOPInstanceUID
    anon_path = os.path.join(UPLOAD_DIR, f"{sop_uid}_anon.dcm")
    npy_path = os.path.join(PROCESSED_DIR, f"{sop_uid}_anon.npy")

    try:
        ds.save_as(anon_path)
        logging.info(f"[Datei] Anonymisierte Datei gespeichert: {anon_path}")
    except Exception as e:
        logging.error(f"[Datei] Fehler beim Speichern der anonymisierten Datei: {anon_path} → {str(e)}")
        raise DICOMProcessingError(f"Fehler beim Speichern der anonymisierten Datei: {str(e)}")

    try:
        np.save(npy_path, pixel_array)
        logging.info(f"[PixelData] Pixel-Array gespeichert unter: {npy_path}")
    except Exception as e:
        logging.error(f"[PixelData] Fehler beim Speichern des Pixel-Arrays: {str(e)}")
        raise DICOMProcessingError(f"Fehler beim Speichern des Pixel-Arrays: {str(e)}")
    
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
    
             
            



  
    

    
    
    #pass
    #db: Session = get_db().__next__()

    # try:
    #     ds = pydicom.dcmread(file_path)
    #     logging.info(f"[Upload] DICOM-Datei erfolgreich gelesen: {file_path}")
    # except InvalidDicomError:
    #     logging.error(f"[Upload] Ungültige DICOM-Datei: {file_path}")
    #     raise ValueError(f"Datei ist kein gültiges DICOM-Format: {file_path}")
    # except Exception as e:
    #     logging.error(f"[Upload] Allgemeiner Fehler beim Lesen der Datei: {file_path} → {str(e)}")
    #     raise

    # ds = anonymize_dicom_fields(ds)
    # logging.info("[Anonymisierung] Anonymisierung abgeschlossen.")

    # run_full_validation(ds, file_path)
    # logging.info("[Validation] Validierung abgeschlossen.")

    # # dicom_hash = generate_dicom_hash(ds)
    # # logging.info(f"[Hash] Hash generiert: {dicom_hash}")

    # upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    # os.makedirs(upload_dir, exist_ok=True)
    # #TODO: hier statt dicom_hash, die SOPInstanceUID der Datei verwenden
    # anon_path = os.path.join(upload_dir, f"{dicom_hash}_anon.dcm")

    # try:
    #     ds.save_as(anon_path)
    #     logging.info(f"[Datei] Anonymisierte Datei gespeichert: {anon_path}")
    # except Exception as e:
    #     logging.error(f"[Datei] Fehler beim Speichern der anonymisierten Datei: {anon_path} → {str(e)}")
    #     raise RuntimeError(f"Fehler beim Speichern der anonymisierten Datei: {str(e)}")

    # try:
    #     #TODO: hier statt dicom_hash, die SOPInstanceUID der Datei verwenden
    #     npy_path = extract_pixel_array(ds, dicom_hash)
    #     logging.info(f"[PixelData] Pixel-Array gespeichert unter: {npy_path}")
    # except Exception as e:
    #     logging.error(f"[PixelData] Fehler beim Speichern des Pixel-Arrays: {str(e)}")
    #     raise RuntimeError(f"Fehler beim Speichern des Pixel-Arrays: {str(e)}")

    # #TO DO: nur für die Datenbank, also noch nicht relevant
    # #metadata = extract_metadata(ds)

    # #TO DO: Speciherung der Metadaten in der Datenbank
    # # try:
    # #     #TO DO: Benutzung von create_dicom aus crud_dicom.py
    # #     #crud_dicom.create_or_replace_dicom_metadata(db, metadata)
    # #     logging.info("[DB] Metadaten erfolgreich in die Datenbank gespeichert.")
    # # except Exception as e:
    # #     logging.error(f"[Upload] Fehler bei DB-Speicherung: {e}")
    # #     raise HTTPException(
    # #         status_code=500,
    # #         detail="Fehler beim Erstellen eines DICOM-Metadatensatzes."
    # #     )

    # return {
    #     "anonymized_file": anon_path,
    #     "pixel_array_file": npy_path

    #     #"metadata": metadata
    # }




#TODO: Tag "modaltity" soll geprüft werden, 
#obs befüllt ist, aber dessen Inhalt auch, 
#aber soll nicht crashen, wenn die Modalität nicht in Valid_Modalities drin ist 
#TODO: Diskutieren, wozu überhaupt dann checken, 
# wenn sowieso alles durchgelassen werden, oder parsen wir diese Info für die Matching Logik?
# def check_modality(ds: Dataset) -> None:
#     """Prüft, ob Modalität unterstützt ist (z. B. CT, MR, etc.)."""
#     VALID_MODALITIES = {"CT", "MR", "XR", "US", "NM", "PT", "DX", "MG", "CR"}

#     modality = getattr(ds, "Modality", "").upper()
#     if modality and modality not in VALID_MODALITIES:
#         #logging.error(f"[Validation] Unbekannte oder ungültige Modalität: {modality}")
#         raise HTTPException(status_code=422, detail=f"Unbekannte oder ungültige Modalität: {modality}.")

    





# def run_full_validation(ds: Dataset, filename: str) -> None:
#     #logging.info(f"[Validation] Starte Validierung der DICOM-Metadaten für Datei: {filename}")
#     #check_compliance(ds, filename)

#     # TODO: Final entscheiden welche Pflichtfelder validiert werden
#     required_tags = {
#         # "PatientID": 2,
#         # "PatientName": 2,
#         # "StudyInstanceUID": 2,
#         # "SeriesInstanceUID": 2,
#         "SOPInstanceUID": 1,
#         "SOPClassUID": 1,
#         "Modality": 1,
#         # "InstanceNumber": 2,
#         # "StudyDate": 2,
#         # "FrameOfReferenceUID": 2,
#         # "SamplesPerPixel": 2,
#         # "PhotometricInterpretation": 2,
#     }

#     # if ds.Modality in {"CT", "MR", "PT"}:
#     #     required_tags["ImagePositionPatient"] = 2
#     #     required_tags["ImageOrientationPatient"] = 2
#     #     required_tags["PixelSpacing"] = 2

#     check_required_tags(ds, required_tags)
#     #check_date_fields(ds)
#     #check_uid_formats(ds)
#     check_modality(ds)
#     check_pixeldata_presence(ds, filename)
#     #check_transfer_syntax(ds)
#     #log_private_tags(ds, filename)
#     logging.info(f"[Validation] DICOM-Metadaten erfolgreich validiert für Datei: {filename}")






