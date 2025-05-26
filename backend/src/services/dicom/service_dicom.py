import os
from dotenv import load_dotenv
import hashlib
import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError
from sqlalchemy.orm import Session
import logging
from fastapi import HTTPException

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)

# DICOM-spezifische Services
from services.dicom.anonymizer import anonymize_dicom_fields
from services.dicom.hasher import generate_dicom_hash
from services.dicom.extractor import extract_pixel_array
from services.dicom.metadata import extract_metadata
from services.dicom.validation import run_full_validation

# Datenbank-Zugriff
from db.crud import crud_dicom
from db.database.database import get_db

# Verarbeitet eine einzelne DICOM-Datei: Validierung → Anonymisierung → Speicherung
def handle_dicom_upload(file_path: str) -> dict:
    db: Session = get_db().__next__()

    try:
        ds = pydicom.dcmread(file_path)
        logging.info(f"[Upload] DICOM-Datei erfolgreich gelesen: {file_path}")
    except InvalidDicomError:
        logging.error(f"[Upload] Ungültige DICOM-Datei: {file_path}")
        raise ValueError(f"Datei ist kein gültiges DICOM-Format: {file_path}")
    except Exception as e:
        logging.error(f"[Upload] Allgemeiner Fehler beim Lesen der Datei: {file_path} → {str(e)}")
        raise

    ds = anonymize_dicom_fields(ds)
    logging.info("[Anonymisierung] Anonymisierung abgeschlossen.")

    run_full_validation(ds, file_path)
    logging.info("[Validation] Validierung abgeschlossen.")

    dicom_hash = generate_dicom_hash(ds)
    logging.info(f"[Hash] Hash generiert: {dicom_hash}")

    upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    anon_path = os.path.join(upload_dir, f"{dicom_hash}_anon.dcm")

    try:
        ds.save_as(anon_path)
        logging.info(f"[Datei] Anonymisierte Datei gespeichert: {anon_path}")
    except Exception as e:
        logging.error(f"[Datei] Fehler beim Speichern der anonymisierten Datei: {anon_path} → {str(e)}")
        raise RuntimeError(f"Fehler beim Speichern der anonymisierten Datei: {str(e)}")

    try:
        npy_path = extract_pixel_array(ds, dicom_hash)
        logging.info(f"[PixelData] Pixel-Array gespeichert unter: {npy_path}")
    except Exception as e:
        logging.error(f"[PixelData] Fehler beim Speichern des Pixel-Arrays: {str(e)}")
        raise RuntimeError(f"Fehler beim Speichern des Pixel-Arrays: {str(e)}")

    metadata = extract_metadata(ds)

    try:
        crud_dicom.create_or_replace_dicom_metadata(db, metadata)
        logging.info("[DB] Metadaten erfolgreich in die Datenbank gespeichert.")
    except Exception as e:
        logging.error(f"[Upload] Fehler bei DB-Speicherung: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Erstellen eines DICOM-Metadatensatzes."
        )

    return {
        "anonymized_file": anon_path,
        "pixel_array_file": npy_path,
        "metadata": metadata
    }
