from fastapi import APIRouter, HTTPException
from backend.src.api import KIImageMetadata
from typing import List

router = APIRouter(prefix="/images", tags=["images"])

# Simulierte In-Memory-Datenbank
fake_db = []

@router.post("/upload", response_model=KIImageMetadata)
async def upload_image(image: KIImageMetadata):
    db_image = {
        "id": len(fake_db) + 1,
        "image_name": image.name,
        "image_tag": image.image_tag,
        "description": image.description,
        "image_path": image.image_path,
        "user_id": image.user_id
    }
    fake_db.append(db_image)
    return db_image

@router.get("/", response_model=List[KIImageMetadata])
async def list_images():
    return fake_db

@router.get("/{id}", response_model=KIImageMetadata)
async def get_image(id: int):
    for image in fake_db:
        if image["id"] == id:
            return image
    raise HTTPException(status_code=404, detail="Image not found")

@router.put("/{id}", response_model=KIImageMetadata)
async def update_image(id: int, image: KIImageMetadata):
    for idx, db_image in enumerate(fake_db):
        if db_image["id"] == id:
            updated_image = {
                "id": id,
                "name": image.name,
                "image_tag": image.image_tag,
                "description": image.description,
                "image_path": image.image_path,
                "user_id": image.user_id
            }
            fake_db[idx] = updated_image
            return updated_image
    raise HTTPException(status_code=404, detail="Image not found")

@router.delete("/{id}")
async def delete_image(id: int):
    for idx, db_image in enumerate(fake_db):
        if db_image["id"] == id:
            fake_db.pop(idx)
            return {"message": "Image deleted"}
    raise HTTPException(status_code=404, detail="Image not found")