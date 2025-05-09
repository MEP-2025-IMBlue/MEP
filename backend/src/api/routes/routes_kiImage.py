# FastAPI & Dependency Injection
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends

# Datenbank (SQLAlchemy)
from sqlalchemy.orm import Session
from src.db.database.database import get_db
from src.db.crud import crud_kiImage
from src.db.core.exceptions import NoKIImagesInTheList, KIImageNotFound, DatabaseError

# API Models (Pydantic)
from src.api.py_models.py_models import *

# Services (Image-Logik)
from src.services.image_upload import service_KIImage

# Externe Libraries
import logging
import docker

router = APIRouter(tags=["KI-Image"])
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

@router.get("/ki-images")
async def list_ki_images(db: Session = Depends(get_db)):
    try:
        return crud_kiImage.get_all_ki_images(db)
    except NoKIImagesInTheList as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ki-images/{image_id}", response_model=KIImageMetadata)
async def get_ki_image(image_id: int, db: Session = Depends(get_db)):
    try:
        return crud_kiImage.get_ki_image_by_id(db, image_id)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/ki-images", response_model=KIImageMetadata)
# async def add_ki_image_route(ki_image: KIImageMetadata, db: Session = Depends(get_db)):
#     try:
#         image_data_dict = ki_image.model_dump(exclude_unset=True)
#         return crud_kiImage.create_ki_image(db, image_data_dict)
#     except DatabaseError as e:
#         raise HTTPException(status_code=500, detail=str(e))

# ========================================
# KI-Image lokal hochladen
# ========================================
@router.post("/ki-images/local", response_model=KIImageMetadata)
async def upload_local_ki_image(
    file: UploadFile = File(...),
    image_name: Optional[str] = Form(None),
    image_tag: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        file_bytes = await file.read()
        image_data = service_KIImage.import_local_image(
            file_bytes=file_bytes,
            image_name=image_name,
            image_tag=image_tag
        )
        db_image = crud_kiImage.create_ki_image(db, image_data)
        return db_image
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during local image upload")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# KI-Image von DockerHub hochladen
# ========================================
@router.post("/ki-images/hub", response_model=KIImageMetadata)
async def pull_ki_image(
    image_name: str = Form(...),
    image_tag: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        image_data = service_KIImage.import_hub_repositorie_image(
            image_name=image_name,
            image_tag=image_tag
        )
        db_image = crud_kiImage.create_ki_image(db, image_data)
        return db_image
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during dockerhub pull")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ki-images/{image_id}")
async def delete_ki_image_route(image_id: int, db: Session = Depends(get_db)):
    try:
        deleted_image = crud_kiImage.delete_ki_image(db, image_id)
        return {"message": f"KI-Image mit der ID {image_id} wurde gelöscht."}
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/ki-images/{image_id}", response_model=KIImageMetadata)
async def patch_ki_image(image_id: int, updated_ki_image: KIImageUpdate, db: Session = Depends(get_db)):
    try:
        update_data = updated_ki_image.model_dump(exclude_unset=True)
        return crud_kiImage.update_ki_image(db, image_id, update_data)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))