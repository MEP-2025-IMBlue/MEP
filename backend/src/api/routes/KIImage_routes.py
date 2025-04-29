from fastapi import APIRouter, HTTPException
from backend.src.api import KIImageMetadata
from typing import List

#An M: was ist prefix?
router = APIRouter(prefix="/images", tags=["images"])

# Simulierte In-Memory-Datenbank
fake_db = []

@router.get("/list-KIimages", response_model=List[KIImageMetadata])
async def list_KIimages():
    return fake_db

@router.get("/get-KIimage/{image_id}", response_model=KIImageMetadata)
async def get_KIimage(image_id: int):
    if image_id < 0 or image_id >= len(fake_db):
        pass
    # for image in fake_db:
    #     if image["id"] == id:
    #         return image
    #raise HTTPException(status_code=404, detail="Image not found")

@router.post("/add-KIimage")
async def add_KIimage(KIimage: KIImageMetadata):
    fake_db.append(KIimage)
    return KIimage

@router.delete("/delete-KIimage/{image_id}")
async def delete_KIimage(image_id: int):
    for idx, KIImageMetadata in enumerate(fake_db):
        if KIImageMetadata["image_id"] == image_id:
            fake_db.pop(idx)
            return {"message": "Image deleted"}
    # for idx, db_image in enumerate(fake_db):
    #     if db_image["id"] == id:
    #         fake_db.pop(idx)
    #         return {"message": "Image deleted"}
    raise HTTPException(status_code=404, detail="KI-Image with {image_id} not found")

# @router.put("/{id}", response_model=KIImageMetadata)
# async def update_image(id: int, image: KIImageMetadata):
#     for idx, db_image in enumerate(fake_db):
#         if db_image["id"] == id:
#             updated_image = {
#                 "id": id,
#                 "name": image.name,
#                 "image_tag": image.image_tag,
#                 "description": image.description,
#                 "image_path": image.image_path,
#                 "user_id": image.user_id
#             }
#             fake_db[idx] = updated_image
#             return updated_image
#     raise HTTPException(status_code=404, detail="Image not found")

