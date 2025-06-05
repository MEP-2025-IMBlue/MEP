from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from typing import List, Optional
from docker.errors import NotFound, APIError
from src.services.container_management.service_container import ContainerService
from src.utils.event_logger import log_event  # JSON-basiertes Logging
import os

# Pydantic-Modell für die Rückgabe von Container-Logs
class LogResponse(BaseModel):
    logs: List[str]

# Pydantic-Modell für den Container-Status und Health-Check
class StatusResponse(BaseModel):
    status: str
    health: str

# Router-Konfiguration mit Prefix für alle Container-bezogenen Endpunkte
router = APIRouter(prefix="/containers", tags=["Container Logs"])
container_service = ContainerService()

# Route: Gibt die Logs eines bestimmten Containers zurück
@router.get("/{container_id_or_name}/logs", response_model=LogResponse)
async def get_container_logs(
    container_id_or_name: str,
    tail: int = Query(100, ge=1, le=1000),          # Anzahl der letzten Zeilen
    stdout: bool = Query(True),                    # stdout ein-/ausschalten
    stderr: bool = Query(True),                    # stderr ein-/ausschalten
    timestamps: bool = Query(True),                # Zeitstempel ein-/ausschalten
    user_id: Optional[int] = Query(None)           # Optional: ID des aufrufenden Benutzers
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
async def get_status_and_health(container_id_or_name: str, user_id: Optional[int] = Query(None)):
    try:
        result = container_service.get_container_status_and_health(container_id_or_name)
        log_event("CONTAINER", "get_status_and_health", f"Status für {container_id_or_name} erfolgreich abgefragt", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return result
    except Exception as e:
        log_event("ERROR", "get_status_and_health", f"Fehler beim Statusabruf: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt nur laufende (aktive) Container zurück
@router.get("/list", response_model=List[str])
async def list_containers(user_id: Optional[int] = Query(None)):
    try:
        result = container_service.list_running_containers()
        log_event("CONTAINER", "list_containers", "Laufende Container erfolgreich abgerufen", level="INFO", user_id=user_id)
        return result
    except Exception as e:
        log_event("ERROR", "list_containers", f"Fehler beim Abrufen der Containerliste: {str(e)}", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Containerliste")

# Route: Stoppt einen laufenden Container
@router.post("/{container_id_or_name}/stop")
async def stop_container_route(container_id_or_name: str, user_id: Optional[int] = Query(None)):
    try:
        result = container_service.stop_container(container_id_or_name)
        log_event("CONTAINER", "stop_container_route", f"Container {container_id_or_name} erfolgreich gestoppt", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        log_event("ERROR", "stop_container_route", f"Fehler beim Stoppen des Containers {container_id_or_name}: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt aktuelle Ressourceninformationen eines Containers zurück (CPU, RAM)
@router.get("/{container_id_or_name}/resources")
async def get_container_resources(container_id_or_name: str, user_id: Optional[int] = Query(None)):
    try:
        result = container_service.get_container_resource_usage(container_id_or_name)
        log_event("CONTAINER", "get_container_resources", f"Ressourcen für Container {container_id_or_name} erfolgreich abgerufen", level="INFO", container_id=container_id_or_name, user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        log_event("ERROR", "get_container_resources", f"Fehler beim Abrufen der Ressourcen: {str(e)}", level="ERROR", container_id=container_id_or_name, user_id=user_id)
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt alle Container zurück (laufende + gestoppte)
@router.get("/all")
async def list_all_containers(user_id: Optional[int] = Query(None)):
    try:
        result = container_service.list_containers()
        log_event("CONTAINER", "list_all_containers", "Alle Container erfolgreich abgerufen", level="INFO", user_id=user_id)
        return JSONResponse(content=result)
    except Exception as e:
        log_event("ERROR", "list_all_containers", f"Fehler beim Abrufen aller Container: {str(e)}", level="ERROR", user_id=user_id)
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen aller Container")