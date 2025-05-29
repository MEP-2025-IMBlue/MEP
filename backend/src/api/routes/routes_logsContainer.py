from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from typing import List
from docker.errors import NotFound, APIError
from src.services.container_management.service_container import ContainerService
from src.utils.event_logger import log_event  # JSON-basiertes Logging

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
    timestamps: bool = Query(True)
):
    try:
        # Container-Logs abrufen
        logs = container_service.get_container_logs(
            container_id_or_name,
            tail=tail,
            stdout=stdout,
            stderr=stderr,
            timestamps=timestamps
        )
        # Erfolgreiches Loggen des Abrufs
        log_event("CONTAINER", "get_container_logs", f"Logs von {container_id_or_name} erfolgreich abgerufen", level="INFO")
        return {"logs": logs.splitlines()}
    except NotFound:
        # Fehler: Container nicht gefunden
        log_event("ERROR", "get_container_logs", f"Container nicht gefunden: {container_id_or_name}", level="ERROR")
        raise HTTPException(status_code=404, detail=f"Container '{container_id_or_name}' nicht gefunden.")
    except APIError as e:
        # Fehler: Docker API-Problem
        log_event("ERROR", "get_container_logs", f"Docker API Fehler: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail="Docker API-Fehler")
    except Exception as e:
        # Fehler: Unbekannter Fehler beim Abruf
        log_event("ERROR", "get_container_logs", f"Unbekannter Fehler: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail="Interner Serverfehler")

# Route: Gibt Status- und Gesundheitsinformationen eines Containers zurück
@router.get("/{container_id_or_name}/status", response_model=StatusResponse)
async def get_status_and_health(container_id_or_name: str):
    try:
        # Statusinformationen abrufen
        result = container_service.get_container_status_and_health(container_id_or_name)
        # Erfolgreiches Loggen des Statusabrufs
        log_event("CONTAINER", "get_status_and_health", f"Status für {container_id_or_name} erfolgreich abgefragt", level="INFO")
        return result
    except Exception as e:
        # Fehler beim Statusabruf loggen
        log_event("ERROR", "get_status_and_health", f"Fehler beim Statusabruf: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt nur laufende Container zurück
@router.get("/list", response_model=List[str])
async def list_containers():
    try:
        # Laufende Container abrufen
        result = container_service.list_running_containers()
        # Erfolgreiches Loggen der Containerliste
        log_event("CONTAINER", "list_containers", "Laufende Container erfolgreich abgerufen", level="INFO")
        return result
    except Exception as e:
        # Fehler beim Abrufen der Containerliste loggen
        log_event("ERROR", "list_containers", f"Fehler beim Abrufen der Containerliste: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Containerliste")

# Route: Stoppt einen laufenden Container
@router.post("/{container_id_or_name}/stop")
async def stop_container_route(container_id_or_name: str):
    try:
        # Container stoppen
        result = container_service.stop_container(container_id_or_name)
        # Erfolgreiches Loggen des Stop-Vorgangs
        log_event("CONTAINER", "stop_container_route", f"Container {container_id_or_name} erfolgreich gestoppt", level="INFO")
        return JSONResponse(content=result)
    except Exception as e:
        # Fehler beim Stoppen loggen
        log_event("ERROR", "stop_container_route", f"Fehler beim Stoppen des Containers {container_id_or_name}: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt Ressourceninformationen (CPU, RAM) eines Containers zurück
@router.get("/{container_id_or_name}/resources")
async def get_container_resources(container_id_or_name: str):
    try:
        # Ressourceninformationen abrufen
        result = container_service.get_container_resource_usage(container_id_or_name)
        # Erfolgreiches Loggen der Ressourcennutzung
        log_event("CONTAINER", "get_container_resources", f"Ressourcen für Container {container_id_or_name} erfolgreich abgerufen", level="INFO")
        return JSONResponse(content=result)
    except Exception as e:
        # Fehler beim Abrufen der Ressourcen loggen
        log_event("ERROR", "get_container_resources", f"Fehler beim Abrufen der Ressourcen: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# Route: Gibt alle Container (laufend und gestoppt) zurück
@router.get("/all")
async def list_all_containers():
    try:
        # Alle Container abrufen
        result = container_service.list_containers()
        # Erfolgreiches Loggen aller Container
        log_event("CONTAINER", "list_all_containers", "Alle Container erfolgreich abgerufen", level="INFO")
        return JSONResponse(content=result)
    except Exception as e:
        # Fehler beim Abrufen aller Container loggen
        log_event("ERROR", "list_all_containers", f"Fehler beim Abrufen aller Container: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen aller Container")
