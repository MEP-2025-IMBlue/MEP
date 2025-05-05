from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict


# ------------------------------------------------------------
# Abschnitt: KIImageMetadata

class KIImageMetadata(BaseModel):
    image_id: Optional[int] = None
    image_name: str
    image_tag: str
    description: Optional[str] = None
    image_path: Optional[str] = None  # Für Docker Hub-Images
    local_image_name: Optional[str] = None  # Für lokale Images
    provider_id: Optional[int] = None

class KIImageUpdate(BaseModel):
    image_name: Optional[str]
    tag: Optional[str]
    repository: Optional[str] 
    created_at: Optional[str] 
    size: Optional[int]
    architecture: Optional[Literal["amd64", "arm64", "arm/v7"]] 
    os: Optional[Literal["linux", "windows"]]

class ImageUpload(BaseModel):
    name: str
    image_tag: str
    description: Optional[str] = None
    user_id: Optional[int] = None

# ------------------------------------------------------------
# Abschnitt: Container

class ContainerCreate(BaseModel):
    image_path: Optional[str] = None  # Optional, default=None
    local_image_name: Optional[str] = None  # Optional, default=None
    container_name: str
    env_vars: Dict[str, str]

class ContainerResponse(BaseModel):
    container_id: str
    name: str
    status: str