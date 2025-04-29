from pydantic import BaseModel, Field
from typing import Optional, Literal


class KIImageMetadata(BaseModel):
    image_id: str
    image_name: str = Field(..., title="Image Name", max_length=255)
    tag: str = Field(..., title="Image Tag", max_length=128)
    repository: str = Field(..., title="Repository", max_length=255)
    created_at: str = Field(..., title="Creation Timestamp", example="2025-04-14T")
    size: int = Field(..., title="Image Size in Bytes")
    architecture: Optional[Literal["amd64", "arm64", "arm/v7"]] = Field(None, title="CPU Architecture")
    os: Optional[Literal["linux", "windows"]] = Field(None, title="Operating System")