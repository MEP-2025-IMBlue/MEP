from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from src.api.py_models.py_models import *
from src.db.database.database import get_db
from src.db.crud import crud_kiImage
from src.db.core.exceptions import NoKIImagesInTheList, KIImageNotFound, DatabaseError
import logging
import json
import tempfile
import docker
import os
from typing import List
from pydantic import ValidationError

router = APIRouter(tags=["KI-Image"])
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

@router.get("/ki-images", response_model= List[KIImageMetadata], description="""
Returns a list of all currently stored KI-images from the database.
-> If at least one KI-image exists, the response is a JSON array of image objects.
-> If no KI-images are found, an error with status code 404 is returned.
-> If a database error occurs, an error with status code 500 is returned.
""",
    responses={
        200: {"description": "List of stored KI-images"},
        404: {"description": "No KI-images found in the database"},
        500: {"description": "Internal server error due to a database issue"}
    })
async def list_ki_images(db: Session = Depends(get_db)):
    try:
        return crud_kiImage.get_all_ki_images(db)
    except NoKIImagesInTheList as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ki-images/{image_id}", response_model=KIImageMetadata, description="""
Retrieves a single KI-image by its unique ID.
-> If the KI-image with the specified `image_id` exists, its metadata is returned as a JSON object.  
-> If no KI-image is found with the given ID, a 404 error is returned.  
-> If a database error occurs during the query, a 500 error is returned.
""",
    responses={
        200: {"description": "Metadata of the requested KI-image"},
        404: {"description": "No KI-image found with the given ID"},
        500: {"description": "Internal server error due to a database issue"}
    })
async def get_ki_image(image_id: int, db: Session = Depends(get_db)):
    try:
        return crud_kiImage.get_ki_image_by_id(db, image_id)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ki-images", response_model=KIImageMetadata, description="""
Creates a new KI-Image entry in the database.  
-> The request must contain all required fields (`image_name`, `image_tag`, and `image_provider_id`).  
-> If any field is invalid (e.g., empty strings for `image_name` or `image_tag`), a 422 error is returned.
""",
    responses={
        200: {"description": "KI-Image successfully created"},
        422: {"description": "Validation failed – empty or invalid fields"},
        500: {"description": "Database error while creating the KI-Image"}
    })
async def add_ki_image_route(ki_image: KIImageMetadata, db: Session = Depends(get_db)):
    try:
        image_data_dict = ki_image.model_dump(exclude_unset=True)
        return crud_kiImage.create_ki_image(db, image_data_dict)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ki-images/{image_id}", description="""
Deletes a specific KI-Image from the database by its ID.
-> If a KI-Image with the given `image_id` exists, it is removed. 
-> If no KI-Image is found with the specified ID, a 404 error is returned.  
-> If a database error occurs during deletion, a 500 error is returned.
""",
    responses={
        200: {"description": "KI-Image successfully deleted"},
        404: {"description": "No KI-Image found with the given ID"},
        500: {"description": "Internal server error due to a database issue"}
    })
async def delete_ki_image_route(image_id: int, db: Session = Depends(get_db)):
    try:
        deleted_image = crud_kiImage.delete_ki_image(db, image_id)
        return {"message": f"KI-Image mit der ID {image_id} wurde gelöscht."}
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/ki-images/{image_id}", response_model=KIImageMetadata, description="""
Updates the metadata of a KI-Image by its ID. 
-> Only the fields provided in the request will be updated.  
-> If the KI-Image does not exist, a 404 error is returned.  
-> If any provided values are invalid (e.g., empty strings for image_name or image_tag), a 422 error is returned.
""",
    responses={
        200: {"description": "KI-Image metadata successfully updated"},
        404: {"description": "KI-Image with given ID not found"},
        422: {"description": "Validation failed – empty or invalid fields"},
        500: {"description": "Database error during update"}
    })
async def patch_ki_image(image_id: int, updated_ki_image: KIImageUpdate, db: Session = Depends(get_db)):
    try:
        update_data = updated_ki_image.model_dump(exclude_unset=True)
        return crud_kiImage.update_ki_image(db, image_id, update_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

