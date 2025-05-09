# FastAPI & Dependency Injection
from fastapi import APIRouter, HTTPException, Form, Depends

# Datenbank (SQLAlchemy)
from sqlalchemy.orm import Session
from src.db.database.database import get_db
from src.db.core.exceptions import DatabaseError

# API Models (Pydantic)
from src.api.py_models.py_models import ContainerResponse 

# Services (Docker-Logik)
from src.services.container_management.service_container import ContainerService

# Externe Libraries
import docker
import logging

# Typisierung
from typing import List, Optional

router = APIRouter(tags=["Container"])
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

#Instanz der Service-Klasse
container_service = ContainerService()

@router.post("/containers/start", response_model=ContainerResponse)
async def start_user_container(
    user_id: int = Form(...),
    image_id: int = Form(...),
    container_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        container_response = container_service.start_user_container(
            db=db,
            user_id=user_id,
            image_id=image_id,
            optional_container_name=container_name
        )
        return container_response
    except docker.errors.ImageNotFound:
        raise HTTPException(status_code=404, detail="Image not found in Docker daemon.")
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during container start")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ========================================
# Einzelnen Container abrufen (per Name)
# ========================================
@router.get("/containers/by-name/{container_name}", response_model=ContainerResponse)
async def get_container_by_name(container_name: str):
    try:
        container_data = container_service.get_container_status(container_name)
        return ContainerResponse(**container_data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        logger.exception("Unexpected error during get_container_by_name")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
# ========================================
# Liste aller Container (optional filterbar nach user_id)
# ========================================
@router.get("/containers/", response_model=List[ContainerResponse])
async def list_containers(user_id: Optional[int] = None):
    try:
        containers = container_service.list_containers(user_id=user_id)
        return [ContainerResponse(**c) for c in containers]
    except Exception as e:
        logger.exception("Unexpected error during list_containers")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# ========================================
# Container stoppen (per Name oder ID)
# ========================================
@router.post("/containers/{container_id_or_name}/stop", response_model=ContainerResponse)
async def stop_container(container_id_or_name: str):
    try:
        result = container_service.stop_container(container_id_or_name)
        return ContainerResponse(**result)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        logger.exception("Unexpected error during stop_container")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
# ========================================
# Container löschen (per Name oder ID)
# ========================================
@router.delete("/containers/{container_id_or_name}", response_model=ContainerResponse)
async def delete_container(container_id_or_name: str):
    try:
        result = container_service.remove_container(container_id_or_name)
        return ContainerResponse(**result)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        logger.exception("Unexpected error during delete_container")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")