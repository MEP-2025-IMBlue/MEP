from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from typing import List
import logging
from docker.errors import NotFound, APIError
from src.services.container_management.service_container import ContainerService

# Pydantic response models
class LogResponse(BaseModel):
    logs: List[str]

class StatusResponse(BaseModel):
    status: str
    health: str

# Router Setup
router = APIRouter(prefix="/containers", tags=["Container Logs"])
logger = logging.getLogger(__name__)
container_service = ContainerService()

@router.get(
    "/{container_id_or_name}/logs",
    response_model=LogResponse,
    description="Gibt die letzten Log-Zeilen eines Containers zurück.",
    responses={
        200: {"description": "Log erfolgreich zurückgegeben"},
        404: {"description": "Container nicht gefunden"},
        500: {"description": "Interner Serverfehler während der Log-Auswertung"}
    }
)
async def get_container_logs(
    container_id_or_name: str,
    tail: int = Query(100, ge=1, le=1000),
    stdout: bool = Query(True, description="Nur stdout loggen"),
    stderr: bool = Query(True, description="Nur stderr loggen"),
    timestamps: bool = Query(True, description="Zeitstempel anzeigen")
):
    """
    Gibt die letzten `tail` Zeilen der Logs eines Docker-Containers zurück.
    Optionale Filter: stdout, stderr, timestamps.
    """
    try:
        logs = container_service.get_container_logs(
            container_id_or_name,
            tail=tail,
            stdout=stdout,
            stderr=stderr,
            timestamps=timestamps
        )
        return {"logs": logs.splitlines()}
    except NotFound:
        raise HTTPException(status_code=404, detail=f"Container '{container_id_or_name}' nicht gefunden.")
    except APIError as e:
        logger.error(f"[ContainerLogs] Docker API error bei {container_id_or_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Docker API-Fehler")
    except Exception as e:
        logger.exception(f"[ContainerLogs] Unbekannter Fehler bei {container_id_or_name}")
        raise HTTPException(status_code=500, detail="Interner Serverfehler")

# Route: Status und Health eines Containers
@router.get(
    "/{container_id_or_name}/status",
    response_model=StatusResponse,
    description="Gibt den Status und Health-Zustand eines Containers zurück.",
    responses={
        200: {"description": "Status erfolgreich zurückgegeben"},
        500: {"description": "Fehler beim Statusabruf"}
    }
)
async def get_status_and_health(container_id_or_name: str):
    """
    Gibt den aktuellen Docker-Status (z. B. running, exited) und
    den Health-Status (z. B. healthy, unhealthy) eines Containers zurück.
    """
    try:
        result = container_service.get_container_status_and_health(container_id_or_name)
        return result
    except Exception as e:
        logger.exception("[ContainerStatus] Fehler beim Statusabruf")
        raise HTTPException(status_code=500, detail=str(e))

# Route: Liste aller laufenden Container
@router.get(
    "/list",
    response_model=List[str],
    description="Gibt eine Liste aller laufenden Container zurück.",
    responses={
        200: {"description": "Containerliste erfolgreich zurückgegeben"},
        500: {"description": "Fehler beim Abrufen der Containerliste"}
    }
)
async def list_containers():
    """
    Gibt eine Liste aller laufenden Container zurück.
    """
    try:
        return container_service.list_running_containers()
    except Exception as e:
        logger.exception("[ContainerList] Fehler beim Abrufen der Container")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Containerliste")
@router.post(
    "/{container_id_or_name}/stop",
    summary="Stoppt einen Container",
    response_description="Information über den gestoppten Container",
    responses={
        200: {"description": "Container erfolgreich gestoppt"},
        404: {"description": "Container nicht gefunden"},
        500: {"description": "Fehler beim Stoppen des Containers"}
    }
)
async def stop_container_route(container_id_or_name: str):
    """
    Stoppt einen Docker-Container mit gegebener ID oder Name.
    """
    try:
        result = container_service.stop_container(container_id_or_name)
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception("[ContainerStop] Fehler beim Stoppen")
        raise HTTPException(status_code=500, detail=str(e))
@router.get(
    "/{container_id_or_name}/resources",
    summary="Live-Ressourcennutzung eines Containers",
    description="Zeigt CPU- und Speicherverbrauch eines Containers an.",
    responses={
        200: {"description": "Ressourcennutzung erfolgreich abgerufen"},
        404: {"description": "Container nicht gefunden"},
        500: {"description": "Fehler beim Ressourcenabruf"}
    }
)
async def get_container_resources(container_id_or_name: str):
    try:
        result = container_service.get_container_resource_usage(container_id_or_name)
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception("[ContainerResources] Fehler beim Abrufen")
        raise HTTPException(status_code=500, detail=str(e))
@router.get(
    "/all",
    summary="Liste aller Container (laufend + gestoppt)",
    description="Gibt eine Liste aller vorhandenen Container zurück – egal ob laufend oder gestoppt.",
    responses={
        200: {"description": "Alle Container erfolgreich zurückgegeben"},
        500: {"description": "Fehler beim Abrufen der Container"}
    }
)
async def list_all_containers():
    """
    Gibt eine Liste aller Docker-Container zurück – unabhängig vom Status.
    """
    try:
        result = container_service.list_containers()
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception("[ContainerListAll] Fehler beim Abrufen aller Container")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen aller Container")
