from pydantic import BaseModel
from typing import Dict, Optional

class ContainerCreate(BaseModel):
    image_path: Optional[str] = None  # Optional, default=None
    local_image_name: Optional[str] = None  # Optional, default=None
    container_name: str
    env_vars: Dict[str, str]

class ContainerResponse(BaseModel):
    container_id: str
    name: str
    status: str