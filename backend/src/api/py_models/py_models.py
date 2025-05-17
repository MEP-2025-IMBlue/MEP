# py_models.py
# ----------------------------------------------
# Enthält alle Pydantic-Modelle zur Validierung und Serialisierung
# für die FastAPI-Endpunkte 

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


# ========================================
# KIImageMetadata: Repräsentation aus db_models.py
# ========================================
class KIImageMetadata(BaseModel):
    image_id: int
    image_name: str
    image_tag: str
    image_description: Optional[str] = None
    image_reference: Optional[str] = None
    image_provider_id: int
    image_created_at: datetime  # ✅ NEU hinzugefügt

    class Config:
        from_attributes = True # betrifft nur die Ausgabe, wenn FastAPI ein SQLAlchemy-Objekt als response_model in JSON umwandelt.

# ========================================
# KIImageUpdate: Für PATCH/PUT-Endpunkte
# ========================================
class KIImageUpdate(BaseModel):
    image_name: Optional[str] = None
    image_tag: Optional[str] = None
    image_description: Optional[str] = None
    image_reference: Optional[str] = None
    image_provider_id: Optional[int] = None

    @field_validator("image_name", "image_tag")
    @classmethod
    def no_empty_strings(cls, value, info):
        if value is not None and value.strip() == "":
            raise ValueError(f"{info.field_name} must not be empty")
        return value
    
    class Config:
        from_attributes = True


# ========================================
# DICOMMetadata: DICOM-Modell aus db_models.py
# ========================================
class DICOMMetadata(BaseModel):
    dicom_id: int
    dicom_uuid: str
    dicom_modality: Optional[str] = None
    dicom_body_part_examined: Optional[str] = None
    dicom_study_description: Optional[str] = None
    dicom_model: Optional[str] = None

    class Config:
        from_attributes = True


# ========================================
# ImageUpload 
# ========================================
class ImageUpload(BaseModel):
    image_data: str


# ========================================
# ContainerResponse 
# ========================================
class ContainerResponse(BaseModel):
    container_id: str #VON INT AUF STR GEÄNDERT
    name: str
    status: str #STATUS HINZUGEFÜGT

