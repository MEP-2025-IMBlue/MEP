# py_models.py
# ----------------------------------------------
# Enthält alle Pydantic-Modelle zur Validierung und Serialisierung
# für die FastAPI-Endpunkte

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator, Field


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
# ImageUpload 
# ========================================
class ImageUpload(BaseModel):
    image_data: str

# ========================================
# ContainerResponse 
# ========================================
class ContainerResponse(BaseModel):

    container_id: str
    status: str

# ========================================
# DICOMMetadata: DICOM-Modell
# ========================================
#TO DO: Attribute ändern, also final entscheiden, was wir in der Datenbank ZUR STATISTIK specihern wollen 
class DICOMMetadata(BaseModel):
    """
    Pydantic-Modell für DSGVO-konforme DICOM-Metadaten.
    """
    dicom_id: int
    dicom_modality: Optional[str] = None
    dicom_sop_class_uid: Optional[str] = None
    dicom_manufacturer: Optional[str] = None
    dicom_rows: Optional[int] = None
    dicom_columns: Optional[int] = None
    dicom_bits_allocated: Optional[int] = None
    dicom_photometric_interpretation: Optional[str] = None
    dicom_transfer_syntax_uid: Optional[str] = None
    dicom_file_path: Optional[str] = None
    dicom_created_at: datetime  # NEU hinzugefügt


    class Config:
        from_attributes = True

# ==================================================
# UploadResultItem: Upload-Modell der DICOM-Datei
# ==================================================
class UploadResultItem(BaseModel):
    """
    Ergebnis für eine einzelne DICOM-Datei.
    """
    file: Optional[str] = Field(None, description="Dateiname der Originaldatei")
    error: Optional[str] = Field(None, description="Fehlermeldung, falls Verarbeitung fehlgeschlagen")

class UploadDICOMResponseModel(BaseModel):
    """
    Antwortmodell für den Upload-Endpunkt.
    """
    message: str = Field(..., description="Statusmeldung zur Verarbeitung")
    data: List[UploadResultItem] = Field(..., description="Liste der Ergebnisse pro Datei")