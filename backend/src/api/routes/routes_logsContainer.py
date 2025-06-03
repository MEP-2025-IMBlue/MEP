from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from typing import List, Optional
from docker.errors import NotFound, APIError
from src.services.container_management.service_container import ContainerService
from src.utils.event_logger import log_event  # JSON-basiertes Logging
import os  # ← log okuma için gerekli

# Pydantic-Modelle für API-Antworten
class LogResponse(BaseModel):
    logs: List[str]

class StatusResponse(BaseModel):
    status: str
    health: str

# Router-Konfiguration
router = APIRouter(prefix="/containers", tags=["Container Logs"])
container_service = ContainerService()

# Route: Gibt die Logs eines Containers zurück
@router.get("/{container_id_or_name}/logs", response_model=LogResponse)
async def get_container_logs(
    container_id_or_name: str,
    tail: int = Query(100, ge=1, le=1000),
    stdout: bool = Query(True),
    stderr: bool = Query(True),
    timestamps: bool = Query(True),
    user_id: Optional[int] = Query(None)  # <<< EKLENDİ
):
    try:
        logs = container_service.get_container_logs(
            container_id_or_name,
            tail=tail,
            stdout=stdout,
            stderr=stderr,
            timestamps=timestamps
        )
        log_event("CONTAINER", "get_container_logs", f"Logs von {container_id_or_name} erfolgreich abgerufen", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return {"logs": logs.splitlines()}
    except NotFound:
        log_event("CONTAINER", "get_container_logs", f"Container nicht gefunden: {container_id_or_name}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=404, detail=f"Container '{container_id_or_name}' nicht gefunden.")
    except APIError as e:
        log_event("CONTAINER", "get_container_logs", f"Docker API Fehler: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail="Docker API-Fehler")
    except Exception as e:
        log_event("CONTAINER", "get_container_logs", f"Unbekannter Fehler: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail="Interner Serverfehler")

# Route: Gibt Status- und Gesundheitsinformationen eines Containers zurück
@router.get("/{container_id_or_name}/status", response_model=StatusResponse)
async def get_status_and_health(container_id_or_name: str, user_id: Optional[int] = Query(None)):  # <<< EKLENDİ
    try:
        result = container_service.get_container_status_and_health(container_id_or_name)
        log_event("CONTAINER", "get_status_and_health", f"Status für {container_id_or_name} erfolgreich abgefragt", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return result
    except Exception as e:
        log_event("ERROR", "get_status_and_health", f"Fehler beim Statusabruf: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt nur laufende Container zurück
@router.get("/list", response_model=List[str])
async def list_containers(user_id: Optional[int] = Query(None)):  # <<< EKLENDİ
    try:
        result = container_service.list_running_containers()
        log_event("CONTAINER", "list_containers", "Laufende Container erfolgreich abgerufen", level="INFO", user_id=user_id)
        return result
    except Exception as e:
        log_event("ERROR", "list_containers", f"Fehler beim Abrufen der Containerliste: {str(e)}", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Containerliste")

# Route: Stoppt einen laufenden Container
@router.post("/{container_id_or_name}/stop")
async def stop_container_route(container_id_or_name: str, user_id: Optional[int] = Query(None)):  # <<< EKLENDİ
    try:
        result = container_service.stop_container(container_id_or_name)
        log_event("CONTAINER", "stop_container_route", f"Container {container_id_or_name} erfolgreich gestoppt", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        log_event("ERROR", "stop_container_route", f"Fehler beim Stoppen des Containers {container_id_or_name}: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt Ressourceninformationen (CPU, RAM) eines Containers zurück
@router.get("/{container_id_or_name}/resources")
async def get_container_resources(container_id_or_name: str, user_id: Optional[int] = Query(None)):  # <<< EKLENDİ
    try:
        result = container_service.get_container_resource_usage(container_id_or_name)
        log_event("CONTAINER", "get_container_resources", f"Ressourcen für Container {container_id_or_name} erfolgreich abgerufen", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        log_event("ERROR", "get_container_resources", f"Fehler beim Abrufen der Ressourcen: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt alle Container (laufend und gestoppt) zurück
@router.get("/all")
async def list_all_containers(user_id: Optional[int] = Query(None)):  # <<< EKLENDİ
    try:
        result = container_service.list_containers()
        log_event("CONTAINER", "list_all_containers", "Alle Container erfolgreich abgerufen", level="INFO", user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        log_event("ERROR", "list_all_containers", f"Fehler beim Abrufen aller Container: {str(e)}", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen aller Container")

# Route: Zeigt strukturierte JSON-Logs an (z. B. für UI-Anzeige)
@router.get("/logs/events")
async def get_logs(limit: int = 5):
    log_path = "logs/events.log"
    if not os.path.exists(log_path):
        return JSONResponse(status_code=404, content={"detail": "Logdatei nicht gefunden."})
    
    with open(log_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Letzte Zeilen abrufen (neuste zuerst)
    last_lines = lines[-limit:] if len(lines) > limit else lines
    return {"logs": last_lines[::-1]}
