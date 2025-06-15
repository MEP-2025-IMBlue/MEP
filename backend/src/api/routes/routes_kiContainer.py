# FastAPI & Dependency Injection
from fastapi import APIRouter, HTTPException, Form, Depends, Query
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
from typing import List

# Strukturierter Logger (JSON)
from src.utils.event_logger import log_event

# Authentifizierung
from src.utils.auth import get_current_user, SYSTEM_USER, User

router = APIRouter(tags=["Container"])
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

container_service = ContainerService()

# ========================================
# Container starten
# ========================================
@router.post("/containers/start", response_model=ContainerResponse)
async def start_user_container(
    image_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start = time.time()
    try:
        container_response = container_service.start_user_container(
            db=db,
            current_user=current_user,
            image_id=image_id,
        )
        log_event("CONTAINER", "start_user_container", f"Containerstart für Image {image_id}", "INFO", user_id=current_user.id)
        return container_response
    except Exception as e:
        log_event("CONTAINER", "start_user_container", f"Fehler: {str(e)}", "ERROR", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        REQUEST_TIME.observe(time.time() - start)

# ========================================
# Container-Liste
# ========================================
@router.get("/containers/", response_model=List[ContainerResponse])
async def list_containers(
    include_stopped: bool = Query(False, description="Auch gestoppte Container anzeigen"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start = time.time()
    try:
        result = container_service.list_containers(
            db=db,
            current_user=current_user,
            include_stopped=include_stopped
        )
        log_event("CONTAINER", "list_containers", f"Containerliste abgerufen (include_stopped={include_stopped})", "INFO", user_id=current_user.id)
        return [ContainerResponse(**c) for c in result]
    except Exception as e:
        log_event("CONTAINER", "list_containers", f"Fehler beim Abrufen der Containerliste: {str(e)}", level="ERROR", user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Containerliste")
    finally:
        REQUEST_TIME.observe(time.time() - start)
# ========================================
# Container stoppen
# ========================================
@router.post("/containers/{container_id}/stop", response_model=ContainerResponse)
async def stop_container(
    container_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start = time.time()
    try:
        result = container_service.stop_container(container_id=container_id, current_user=current_user, db=db)
        log_event("CONTAINER", "stop_container", f"Container gestoppt: {container_id}", "INFO", user_id=current_user.id)
        return ContainerResponse(**result)
    except Exception as e:
        log_event("CONTAINER", "stop_container", f"Fehler: {str(e)}", "ERROR", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        REQUEST_TIME.observe(time.time() - start)

# ========================================
# Container löschen
# ========================================
@router.delete("/containers/{container_id}", response_model=ContainerResponse)
async def delete_container(
    container_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start = time.time()
    try:
        result = container_service.remove_container(container_id=container_id, current_user=current_user, db=db)
        log_event("CONTAINER", "delete_container", f"Container gelöscht: {container_id}", "INFO", user_id=current_user.id)
        return ContainerResponse(**result)
    except Exception as e:
        log_event("CONTAINER", "delete_container", f"Fehler: {str(e)}", "ERROR", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        REQUEST_TIME.observe(time.time() - start)

# ========================================
# Container Stats
# ========================================
@router.get("/containers/{container_id}/stats")
async def get_container_stats(
    container_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start = time.time()
    try:
        return container_service.get_container_resource_usage(container_id=container_id, current_user=current_user, db=db)
    except Exception as e:
        log_event("CONTAINER", "get_container_stats", f"Fehler: {str(e)}", "ERROR", user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Container-Ressourcen konnten nicht abgerufen werden.")
    finally:
        REQUEST_TIME.observe(time.time() - start)

# ========================================
# Metriken für Prometheus
# ========================================
@router.get("/container-metrics")
async def update_container_metrics():
    try:
        db_generator = get_db()
        db = next(db_generator)

        containers = docker_client.containers.list()
        for container in containers:
            try:
                container_service.get_container_resource_usage(
                    container_id=container.id,
                    current_user=SYSTEM_USER,
                    db=db
                )
            except Exception as e:
                logger.warning(f"Fehler bei container_resource_usage ({container.short_id}): {e}")

        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Fehler bei update_container_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Metriken konnten nicht aktualisiert werden.")
    finally:
        try:
            db_generator.close()
        except:
            pass
