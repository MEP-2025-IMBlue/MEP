import os
import hashlib
import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError

def validate_dicom(file_path: str) -> bool:
    try:
        ds = pydicom.dcmread(file_path)
        _ = ds.pixel_array  # prüft auf Bilddaten-Zugriff
        return True
    except (InvalidDicomError, AttributeError):
        return False

def anonymize_dicom(file_path: str) -> pydicom.dataset.FileDataset:
    ds = pydicom.dcmread(file_path)
    
    # Anonymisierung vereinfachter Felder
    for tag in ["PatientName", "PatientID", "PatientBirthDate", "InstitutionName"]:
        if tag in ds:
            ds.data_element(tag).value = "ANONYMIZED"
    
    return ds

def generate_dicom_hash(file_path: str) -> str:
    ds = pydicom.dcmread(file_path)

    hash_input = (
        str(ds.get("StudyInstanceUID", "")) +
        str(ds.get("SeriesInstanceUID", "")) +
        str(ds.get("SOPInstanceUID", "")) +
        ds.pixel_array.tobytes().hex()
    )

    return hashlib.sha256(hash_input.encode()).hexdigest()

def extract_pixel_array(ds: pydicom.dataset.FileDataset, hash_name: str) -> str:
    processed_dir = "/tmp/processed"
    os.makedirs(processed_dir, exist_ok=True)

    array = ds.pixel_array.astype(np.float32)
    out_path = os.path.join(processed_dir, f"{hash_name}_anon.npy")
    np.save(out_path, array)
    return out_path

def handle_dicom_upload(file_path: str) -> dict:
    if not validate_dicom(file_path):
        raise ValueError("Ungültige oder defekte DICOM-Datei")

    # Anonymisierung + Hashing vorbereiten
    ds = anonymize_dicom(file_path)
    dicom_hash = generate_dicom_hash(file_path)

    # Speichere anonymisierte Datei
    os.makedirs("/tmp/uploads", exist_ok=True)
    anon_path = os.path.join("/tmp/uploads", f"{dicom_hash}_anon.dcm")
    ds.save_as(anon_path)

    # Extrahiere Pixel-Array als .npy
    npy_path = extract_pixel_array(ds, dicom_hash)

    return {
        "anonymized_file": anon_path,
        "pixel_array_file": npy_path
    }
