from fastapi import APIRouter, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from src.db.database.database import get_db
from src.api.py_models import py_models
from src.db.crud import crud_container_config
from src.services.container_management import service_configuration
from src.db.core.exceptions import *

router = APIRouter(tags=["Container Configuration"])

@router.post("/ki-images/{image_id}/configure") #response_model=py.models.ContainerConfigInput
async def configure_ki_image(image_id: int, input: py_models.KIUploadCombinedInput, db: Session = Depends(get_db)):
    
    try:
        #Med. Metadaten speichern
        crud_container_config.store_medical_info(db, image_id, input.image_info)

        #Container-Konfig speichern
        val_result = service_configuration.validate_configs(input)
        if (val_result):
            crud_container_config.store_container_config(db, image_id, input.container_config)
        else:
            raise HTTPException(status_code=422)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success", "image_id":image_id}

@router.get("/ki-images/{image_id}/configure", response_model=py_models.ContainerConfigInput)
async def get_configuration(image_id: int, db: Session = Depends(get_db)):
    try:
        return crud_container_config.get_container_config_by_id(db, image_id)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/ki-images/{image_id}/configure", response_model=py_models.ContainerConfigInput)
async def patch_configuration(image_id: int, db: Session = Depends(get_db)):
    try:
        return crud_container_config.patch_container_config_by_id(db, image_id)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ki-images/{image_id}/configure", response_model=py_models.ContainerConfigInput)
async def delete_configuration(image_id: int, db: Session = Depends(get_db)):
    try:
        return crud_container_config.delete_container_config_by_id(db, image_id)
    except KIImageNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))