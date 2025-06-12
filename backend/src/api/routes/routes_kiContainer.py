# FastAPI & Dependency Injection
from datetime import timezone
from fastapi import APIRouter, HTTPException, Form, Depends
from fastapi.responses import Response

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
import time
from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST


# Prometheus Metrik
from src.utils.metrics import REQUEST_TIME

# Typisierung
from typing import List, Optional

# Strukturierter Logger (JSON)
from src.utils.event_logger import log_event

router = APIRouter(tags=["Container"])
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

#Instanz der Service-Klasse
container_service = ContainerService()

# ========================================
# Starte aus Image einen Container
# ========================================
@router.post("/containers/start", response_model=ContainerResponse)
async def start_user_container(
    user_id: int = Form(...),
    image_id: int = Form(...),
    db: Session = Depends(get_db)
):
    start = time.time()
    try:
        container_response = container_service.start_user_container(
            db=db,
            user_id=user_id,
            image_id=image_id,
        )
        log_event("CONTAINER", "start_user_container", f"Containerstart angefordert für Image {image_id}", level="INFO", user_id=user_id)
        return container_response
    except docker.errors.ImageNotFound:
        log_event("CONTAINER", "start_user_container", f"Image {image_id} nicht gefunden", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=404, detail="Image not found in Docker daemon.")
    except DatabaseError as e:
        log_event("CONTAINER", "start_user_container", f"DB-Fehler beim Start: {str(e)}", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log_event("CONTAINER", "start_user_container", f"Unerwarteter Fehler: {str(e)}", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")  
    finally:
        duration = time.time() - start
        REQUEST_TIME.observe(duration)

# ========================================
# Liste aller Container (optional filterbar nach user_id)
# ========================================
@router.get("/containers/", response_model=List[ContainerResponse])
async def list_containers(user_id: Optional[int] = None):
    start = time.time()
    try:
        containers = container_service.list_containers(user_id=user_id)
        return [ContainerResponse(**c) for c in containers]
    except Exception as e:
        logger.exception("Unexpected error during list_containers")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        duration = time.time() - start
        REQUEST_TIME.observe(duration)

# ========================================
# Container stoppen (per Name oder ID)
# ========================================
@router.post("/containers/{container_id_or_name}/stop", response_model=ContainerResponse)
async def stop_container(container_id_or_name: str, user_id: Optional[int] = Form(None)):
    start = time.time()
    try:
        result = container_service.stop_container(container_id_or_name, user_id=user_id)
        log_event("CONTAINER", "stop_container", f"Container {container_id_or_name} wurde gestoppt", level="INFO", user_id=user_id)
        return ContainerResponse(**result)
    except Exception as e:
        log_event("CONTAINER", "stop_container", f"Fehler beim Stoppen: {str(e)}", level="ERROR", user_id=user_id)
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")   
    finally:
        duration = time.time() - start
        REQUEST_TIME.observe(duration)

# ========================================
# Container löschen (per Name oder ID)
# ========================================
@router.delete("/containers/{container_id_or_name}", response_model=ContainerResponse)
async def delete_container(container_id_or_name: str):
    start = time.time()
    try:
        result = container_service.remove_container(container_id_or_name)
        return ContainerResponse(**result)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        logger.exception("Unexpected error during delete_container")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        duration = time.time() - start
        REQUEST_TIME.observe(duration)

# ========================================
# CPU- und Speicherinformationen eines Containers abrufen
# ========================================
@router.get("/containers/{container_id}/stats")
async def get_container_stats(container_id: str):
    start = time.time()
    try:
        return container_service.get_container_resource_usage(container_id)
    except Exception as e:
        from src.utils.event_logger import log_event
        log_event(
            event_type="ContainerStatsError",
            source="get_container_stats",
            message=f"Fehler beim Abrufen der Stats für Container {container_id}: {str(e)}"
        )
        logger.exception("Fehler bei get_container_stats")
        raise HTTPException(status_code=500, detail="Container-Ressourcen konnten nicht abgerufen werden.")
    finally:
        duration = time.time() - start
        REQUEST_TIME.observe(duration)

# ========================================
# Container-Metriken für Prometheus aktualisieren
# ========================================
@router.get("/container-metrics")
async def update_container_metrics():
    try:
        # Container-Metriken zur CPU- und RAM-Nutzung aktualisieren und im Prometheus-Format ausgeben
        containers = docker_client.containers.list()
        for container in containers:
            try:
                container_service.get_container_resource_usage(container.id, current_user={"role": "system"})
            except Exception as e:
                logger.warning(f"Fehler bei get_container_resource_usage({container.short_id}): {e}")

        # Prometheus-Format ausgeben
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Container-Metriken: {str(e)}")
        raise HTTPException(status_code=500, detail="Container-Metriken konnten nicht aktualisiert werden.")
