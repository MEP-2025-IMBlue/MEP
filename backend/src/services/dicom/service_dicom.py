#TODO: Alle Funktionalitäten für den DICOM-Upload (NICHT Datenbank!!) hier in dieser Datei zusammenführen

import os
from dotenv import load_dotenv
import hashlib
import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError
from sqlalchemy.orm import Session
import logging
from fastapi import HTTPException, File, UploadFile, Depends, APIRouter
from datetime import datetime
from pydicom.dataset import Dataset
from api.py_models.py_models import DICOMMetadata, UploadDICOMResponseModel, UploadResultItem
from db.core.exceptions import *
import shutil, os, uuid, zipfile


# Logging-Konfiguration
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Gültige Modalitäten gemäß DICOM-Standard
VALID_MODALITIES = {"CT", "MR", "XR", "US", "NM", "PT", "DX", "MG", "CR"}

# # DICOM-spezifische Services
# from services.dicom.anonymizer import anonymize_dicom_fields
# from services.dicom.hasher import generate_dicom_hash
# from services.dicom.extractor import extract_pixel_array
# from services.dicom.metadata import extract_metadata
# from services.dicom.validation import run_full_validation

# # Datenbank-Zugriff
# from db.crud import crud_dicom
# from db.database.database import get_db

#TODO: Was ist das?
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")

def receive_file(file: UploadFile = File(...)):
    """Empfangen von Datei. Nachschauen, ob .dcm oder .zip. Wenn ja, Dateiinhalt in tmp_filepath reinschreiben"""
    
    #TODO: Macht diese Zeile hier Sinn?
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    #Schaue nach, ob die empfangene Datei mit dcm oder zip endet
    filename = file.filename.lower()
    if not filename.endswith((".dcm", ".zip")):
        logger.error(f"Invalid file type uploaded: {filename}")
        raise InvalidDICOMFileType(f"Ungültiger Dateityp: '{filename}'. Erlaubt sind nur .dcm oder .zip.")

    #Erzeuge einen temporären Pfad und schreibe dort den Dateiinhalt von file rein 
    tmp_filepath = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.dcm")
    try:
        with open(tmp_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error processing single DICOM file: {str(e)}")
        raise blabla

    #Weiterleitung an die nächsten Funktionen
    if filename.endswith(".dcm"):
        upload_dicom(tmp_filepath)
    elif filename.endswith(".zip"):
        upload_dicom_zip(tmp_filepath)   

# Verarbeitet eine einzelne DICOM-Datei: Validierung → Anonymisierung → Extraktion -> Temporäre Dateispeicherung
def upload_dicom(tmp_filepath:str):
    """Check ob Datei DICOM konform ist. Wenn ja: Anonymisieren, Validieren, Extahieren und speichern"""

    #Schaue nach, ob die Datei DICOM konform ist
    try:
        ds = pydicom.dcmread(tmp_filepath)
        #logging.info(f"[Upload] DICOM-Datei erfolgreich gelesen: {file_path}")
    except InvalidDicomError:
        #TODO: Datei aus tmp_filepath entfernen -> clean up
        raise ValueError("Datei ist kein gültiges DICOM-Format.")
    except Exception as e:
        #logging.error(f"[Upload] Allgemeiner Fehler beim Lesen der Datei: {file_path} → {str(e)}")
        raise blabla
    
    ds = anonymize_dicom_fields(ds)
    # logging.info("[Anonymisierung] Anonymisierung abgeschlossen.")

    
    pass
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

#TODO: final entscheiden, was genau in einer zip-Datei drin ist
def upload_dicom_zip():
    pass

#TODO: final entschieden, was wirklich anonymisiert wird 
# Diese Funktion anonymisiert sensible DICOM-Felder gemäß DSGVO / HIPAA
def anonymize_dicom_fields(ds: pydicom.Dataset) -> pydicom.Dataset:
    """
    Entfernt oder ersetzt personenbezogene Informationen aus dem DICOM-Dataset.
    Alle ersetzten Felder werden mit dem Wert "ANONYMIZED" befüllt und protokolliert.
    """
    tags_to_anonymize = [
        "PatientName",              # Name des Patienten
        "PatientID",                # Interne ID
        #"PatientBirthDate",         # Geburtsdatum
        "InstitutionName",          # Name der Klinik
        "ReferringPhysicianName",   # Überweisender Arzt
        "OtherPatientIDs",          # Weitere IDs
        #"AccessionNumber",          # Zugriffsnummer
        "OperatorsName",            # Bedienername
        "PatientAddress",           # Adresse
        "IssuerOfPatientID",        # ID-Aussteller
        "StudyID"                   # Studiennummer
    ]

    for tag in tags_to_anonymize:
        if tag in ds:
            original_value = str(ds.get(tag, ""))
            ds.data_element(tag).value = "ANONYMIZED"
            logging.info(f"[Anonymizer] Feld '{tag}' anonymisiert (alt: {original_value})")

    return ds

# Diese Funktion extrahiert das Pixel-Array und speichert es als .npy-Datei im angegebenen oder konfigurierten Verzeichnis
def extract_pixel_array(ds: pydicom.Dataset, hash_name: str, output_dir: str = None) -> str:
    """
    Wandelt das DICOM-Bild in ein NumPy-Array um und speichert es im .npy-Format.
    Der Speicherort wird über Umgebungsvariable 'PROCESSED_DIR' oder optionalen Parameter gesteuert.
    """
    if output_dir is None:
        output_dir = os.getenv("PROCESSED_DIR", "/tmp/processed")
        logging.info(f"[Extractor] Verwende Standardverzeichnis: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)

    try:
        array = ds.pixel_array.astype(np.float32)
        logging.info(f"[Extractor] Pixel-Array erfolgreich extrahiert")
    except Exception as e:
        logging.error(f"[Extractor] Fehler beim Extrahieren des Pixel-Arrays: {str(e)}")
        raise ValueError("Pixel array extraction failed") from e

    out_path = os.path.join(output_dir, f"{hash_name}_anon.npy")
    np.save(out_path, array)
    logging.info(f"[Extractor] Pixel-Array gespeichert unter: {out_path}")
    return out_path

def run_full_validation(ds: Dataset, filename: str) -> None:
    logging.info(f"[Validation] Starte Validierung der DICOM-Metadaten für Datei: {filename}")
    #check_compliance(ds, filename)

    # TODO: Final entscheiden welche Pflichtfelder validiert werden
    required_tags = {
        # "PatientID": 2,
        # "PatientName": 2,
        # "StudyInstanceUID": 2,
        # "SeriesInstanceUID": 2,
        "SOPInstanceUID": 1,
        "SOPClassUID": 1,
        "Modality": 1,
        # "InstanceNumber": 2,
        # "StudyDate": 2,
        # "FrameOfReferenceUID": 2,
        # "SamplesPerPixel": 2,
        # "PhotometricInterpretation": 2,
    }

    # if ds.Modality in {"CT", "MR", "PT"}:
    #     required_tags["ImagePositionPatient"] = 2
    #     required_tags["ImageOrientationPatient"] = 2
    #     required_tags["PixelSpacing"] = 2

    check_required_tags(ds, required_tags)
    #check_date_fields(ds)
    #check_uid_formats(ds)
    check_modality(ds)
    check_pixeldata_presence(ds, filename)
    #check_transfer_syntax(ds)
    #log_private_tags(ds, filename)
    logging.info(f"[Validation] DICOM-Metadaten erfolgreich validiert für Datei: {filename}")

#TODO: nur nach Tag 1 prüfen
def check_required_tags(ds: Dataset, required_tags: dict) -> None:
    fehlende_typ1 = []

    for tag, tag_typ in required_tags.items():
        if not hasattr(ds, tag):
            if tag_typ == 1:
                fehlende_typ1.append(tag)
            elif tag_typ == 2:
                logging.warning(f"[Validation] Optionaler Pflichtwert (Type 2) fehlt: {tag}")
            continue

        value = getattr(ds, tag)
        if tag_typ == 1 and (value is None or str(value).strip() == ""):
            fehlende_typ1.append(tag)
        elif tag_typ == 2 and (value is None or str(value).strip() == ""):
            logging.warning(f"[Validation] {tag} ist leer – erlaubt, aber protokolliert.")

    if fehlende_typ1:
        logging.error(f"[Validation] Fehlende Pflichtfelder (Type 1): {fehlende_typ1}")
        raise ValueError(f"Fehlende Pflichtfelder: {', '.join(fehlende_typ1)}")

#TODO: Tag "modaltity" soll geprüft werden, 
#obs befüllt ist, aber dessen Inhalt auch, 
#aber soll nicht crashen, wenn die Modalität nicht in Valid_Modalities drin ist 
def check_modality(ds: Dataset) -> None:
    modality = getattr(ds, "Modality", "").upper()
    if modality and modality not in VALID_MODALITIES:
        logging.error(f"[Validation] Unbekannte oder ungültige Modalität: {modality}")
        raise HTTPException(status_code=422, detail=f"Unbekannte oder ungültige Modalität: {modality}.")
    
#TODO: Final entscheiden ob man die braucht oder nicht
def check_pixeldata_presence(ds: Dataset, filename: str) -> None:
    if not hasattr(ds, "PixelData"):
        logging.error(f"[Validation] Fehlender 'PixelData' in Datei: {filename}")
        raise HTTPException(status_code=422, detail="Fehlender 'Pixel Data' (7FE0,0010) Tag.")
    #verify_pixeldata_consistency(ds, filename)




