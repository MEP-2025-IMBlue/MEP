"""
py_models.py
-------------
Definiert die Pydantic-Modelle für Validierung und Serialisierung der API-Daten.
Pfad: backend/src/api/py_models.py
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

class KIImageMetadata(BaseModel):
    """
    Pydantic-Modell für vollständige Image-Metadaten.
    """
    image_id: str
    image_name: str = Field(..., title="Image Name", max_length=255)
    tag: str = Field(..., title="Image Tag", max_length=128)
    repository: str = Field(..., title="Repository", max_length=255)
    created_at: str = Field(..., title="Creation Timestamp", example="2025-04-14T")
    size: int = Field(..., title="Image Size in Bytes")
    architecture: Optional[Literal["amd64", "arm64", "arm/v7"]] = Field(None, title="CPU Architecture")
    os: Optional[Literal["linux", "windows"]] = Field(None, title="Operating System")

class KIImageUpdate(BaseModel):
    """
    Pydantic-Modell für partielle Updates (alle Felder optional).
    """
    image_name: Optional[str]
    tag: Optional[str]
    repository: Optional[str]
    created_at: Optional[str]
    size: Optional[int]
    architecture: Optional[Literal["amd64", "arm64", "arm/v7"]]
    os: Optional[Literal["linux", "windows"]]

