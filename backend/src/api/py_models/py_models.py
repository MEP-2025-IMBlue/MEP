# py_models.py
# ----------------------------------------------
# Enthält alle Pydantic-Modelle zur Validierung und Serialisierung
# für die FastAPI-Endpunkte

from typing import Optional, Literal, Dict
from pydantic import BaseModel


# ========================================
# KIImageMetadata: Repräsentation aus db_models.py
# ========================================
class KIImageMetadata(BaseModel):
    image_id: int
    image_name: str
    image_tag: str
    image_description: Optional[str] = None
    image_path: Optional[str] = None
    image_local_name: Optional[str] = None
    image_provider_id: int

    class Config:
        from_attributes = True # betrifft nur die Ausgabe, wenn FastAPI ein SQLAlchemy-Objekt als response_model in JSON umwandelt.

# ========================================
# KIImageUpdate: Für PATCH/PUT-Endpunkte
# ========================================
class KIImageUpdate(BaseModel):
    image_name: Optional[str] = None
    image_tag: Optional[str] = None
    image_description: Optional[str] = None
    image_path: Optional[str] = None
    image_local_name: Optional[str] = None
    image_provider_id: Optional[int] = None

    class Config:
        from_attributes = True


# ========================================
# DICOMMetadata: DICOM-Modell aus db_models.py
# ========================================
class DICOMMetadata(BaseModel):
    dicom_id: int
    dicom_uuid: str
    dicom_modality: Optional[str] = None

    class Config:
        from_attributes = True


# ========================================
# ImageUpload (noch zu überarbeiten)
# ========================================
# TODO: Struktur, Felder und Beschreibung überarbeiten
class ImageUpload(BaseModel):
    image_data: str


# ========================================
# ContainerCreate (noch zu überarbeiten)
# ========================================
# TODO: Struktur, Felder und Validierungen anpassen
class ContainerCreate(BaseModel):
    container_name: str


# ========================================
# ContainerResponse (noch zu überarbeiten)
# ========================================
# TODO: Struktur, Felder und Rückgabeformat finalisieren
class ContainerResponse(BaseModel):
    container_id: int
    status: str
# ========================================
# UploadResultItem: Ergebnis für eine einzelne DICOM-Datei
# ========================================
from typing import List, Optional
from pydantic import Field

class UploadResultItem(BaseModel):
    anonymized_file: Optional[str] = Field(None, description="Pfad zur anonymisierten DICOM-Datei")
    pixel_array_file: Optional[str] = Field(None, description="Pfad zur gespeicherten .npy-Datei")
    file: Optional[str] = Field(None, description="Dateiname der Originaldatei (bei Fehlern)")
    error: Optional[str] = Field(None, description="Fehlermeldung, falls Verarbeitung fehlgeschlagen ist")

# ========================================
# UploadDICOMResponseModel: Antwortmodell für Upload-Endpunkt
# ========================================
class UploadDICOMResponseModel(BaseModel):
    message: str = Field(..., description="Statusmeldung zur Verarbeitung")
    data: List[UploadResultItem] = Field(..., description="Liste der Ergebnisse pro Datei")


