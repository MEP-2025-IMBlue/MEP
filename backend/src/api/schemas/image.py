from pydantic import BaseModel
from typing import Optional

class DockerImageBase(BaseModel):
    id: Optional[int] = None
    name: str
    image_tag: str
    description: Optional[str] = None
    image_path: Optional[str] = None  # Für Docker Hub-Images
    local_image_name: Optional[str] = None  # Für lokale Images
    user_id: Optional[int] = None

class ImageUpload(BaseModel):
    name: str
    image_tag: str
    description: Optional[str] = None
    user_id: Optional[int] = None