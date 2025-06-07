# py_models.py
# ----------------------------------------------
# Enthält alle Pydantic-Modelle zur Validierung und Serialisierung
# für die FastAPI-Endpunkte

from datetime import datetime
from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, field_validator
from src.api.py_models.enums_or_constants import *


# ========================================
# Py_Models für KI-Images 
# ========================================

class KIImageMetadata(BaseModel):
    """Beim ersten Upload des KI-Images aus Provider. Repräsentiert das DB-Schema aus db_models.py"""
    image_id: int
    image_name: str
    image_tag: str
    #image_description: Optional[str] = None
    image_reference: Optional[str] = None
    image_provider_id: int
    image_created_at: datetime  # ✅ NEU hinzugefügt

    class Config:
        from_attributes = True # betrifft nur die Ausgabe, wenn FastAPI ein SQLAlchemy-Objekt als response_model in JSON umwandelt.

#TODO: Eventuell löschen
class KIImageUpdate(BaseModel):
    """Zum Ändern der Sachen, aber fällt wahrscheinlich aus"""
    image_name: Optional[str] = None
    image_tag: Optional[str] = None
    #image_description: Optional[str] = None
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

class KIImageInfo(BaseModel):
    """Zusätzliche Informationen für die KI-Images, die der Provider beim Konfigurieren mitgibt"""
    image_modality: Optional[ImageModality] = ImageModality.NONE #TODO: Maimuna fragen, welche noch reinkommen
    image_bodypart: Optional[ImageBodypart] = ImageBodypart.NONE #TODO: Maimuna fragen, welche noch reinkommen
    image_purpose: Optional[ImagePurpose] = ImagePurpose.NONE #TODO: Maimuna fragen, welche noch reinkommen
    image_model_description: str

    class Config:
        from_attributes = True # betrifft nur die Ausgabe, wenn FastAPI ein SQLAlchemy-Objekt als response_model in JSON umwandelt.

# ==================================================
# Py_Models für KI-Container
# ==================================================

class ContainerConfigInput(BaseModel):
    """Container Configuration, die vom Provider kommen"""
    #Pflichtfelder für Konfiguration
    #TODO: Detached mode auch hier in py_models?
    input_dir: str #TODO:wie validieren?
    output_dir: str #TODO:wie validieren?
    input_format: InputFormat = InputFormat.NONE #TODO: Maimuna fragen, welche Umwandlungen wir noch können

    #Optionale Felder
    output_format: Optional[OutputFormat] = OutputFormat.NONE #TODO: Maimuna fragen, welche noch reinkommen
    environment: Optional[Dict[str, str]] = None
    run_command: Optional[str] = None
    working_dir: Optional[str]
    volumes: Optional[Dict[str, str]] = None
    entrypoint: Optional[str] = None
    gpu_required: Optional[bool] = None
    #cpu_shares:
    #mem_limit:
    #restart_policy:
    #ports:
    #log_config:

    @field_validator("input_dir", "output_dir")
    @classmethod
    def no_empty_strings(cls, value, info):
        if value is not None and value.strip() == "":
            raise ValueError(f"{info.field_name} must not be empty")
        return value
    
    @field_validator("run_command", "entrypoint")
    @classmethod
    def validate_commands(cls, value, info):
        if value is not None:
            for forbidden in FORBIDDEN_COMMANDS:
                if forbidden in value:
                    raise ValueError(f"'{forbidden}' ist im Feld '{info.field_name}' nicht erlaubt")
        return value
    
    class Config:
        from_attributes = True # betrifft nur die Ausgabe, wenn FastAPI ein SQLAlchemy-Objekt als response_model in JSON umwandelt.
    
class KIUploadCombinedInput(BaseModel):
    """Alle Informationen aus dem Konfigformular kombiniert"""
    #image_id: int #id aus bestehendes Image
    image_info: KIImageInfo
    container_config : ContainerConfigInput

class ContainerResponse(BaseModel):
    """Gibt den Status der KI-Container zurück"""
    container_id: str
    status: str

# ========================================
# Py_Models für DICOM
# ========================================
 
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

class UploadResultItem(BaseModel):
    """
    Ergebnis für eine einzelne DICOM-Datei.
    """
    sop_instance_uid: str
    saved_dicom_path: str
    saved_pixel_array_path: str

class UploadDICOMResponseModel(BaseModel):
    """
    Ergebnis für eine zip-Datei mit DICOM
    """
    message: str
    data: List[UploadResultItem]

# ========================================
# Undefiniert
# ========================================
class ImageUpload(BaseModel):
    image_data: str