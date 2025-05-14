import os
import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError

def validate_dicom(file_path: str) -> bool:
    try:
        ds = pydicom.dcmread(file_path)
        _ = ds.pixel_array  # Testet auf Bilddaten
        return True
    except (InvalidDicomError, AttributeError):
        return False

def anonymize_dicom(file_path: str) -> str:
    ds = pydicom.dcmread(file_path)
    
    # Entfernt sensible Felder (vereinfachte Version)
    for tag in ["PatientName", "PatientID", "PatientBirthDate", "InstitutionName"]:
        if tag in ds:
            ds.data_element(tag).value = "ANONYMIZED"

    anonym_path = file_path.replace(".dcm", "_anon.dcm")
    ds.save_as(anonym_path)
    return anonym_path

def extract_pixel_array(file_path: str) -> str:
    ds = pydicom.dcmread(file_path)
    pixel_array = ds.pixel_array.astype(np.float32)
    
    out_path = file_path.replace(".dcm", ".npy")
    np.save(out_path, pixel_array)
    return out_path

def handle_dicom_upload(file_path: str) -> dict:
    if not validate_dicom(file_path):
        raise ValueError("Ungültige oder defekte DICOM-Datei")

    anonym_path = anonymize_dicom(file_path)
    npy_path = extract_pixel_array(anonym_path)

    return {
        "anonymized_file": anonym_path,
        "pixel_array_file": npy_path
    }
