from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
import logging
from docker.errors import NotFound, APIError
from src.services.container_management.service_container import ContainerService

# Pydantic response model for Swagger documentation
class LogResponse(BaseModel):
    logs: List[str]

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
    tail: int = Query(100, ge=1, le=1000)
):
    """
    Gibt die letzten `tail` Zeilen der Logs eines Docker-Containers zurück.
    """
    try:
        logs = container_service.get_container_logs(container_id_or_name, tail=tail)
        return {"logs": logs.splitlines()}
    except NotFound:
        raise HTTPException(status_code=404, detail=f"Container '{container_id_or_name}' nicht gefunden.")
    except APIError as e:
        logger.error(f"[ContainerLogs] Docker API error bei {container_id_or_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Docker API-Fehler")
    except Exception as e:
        logger.exception(f"[ContainerLogs] Unbekannter Fehler bei {container_id_or_name}")
        raise HTTPException(status_code=500, detail="Interner Serverfehler")


# ➕ Neue Route: Liste aller laufenden Container
@router.get(
    "/list",
    response_model=List[str],
    description="Gibt eine Liste aller laufenden Container zurück.",
    responses={
        200: {"description": "Containerliste erfolgreich zurückgegeben"},
        500: {"description": "Fehler beim Abrufen der Containerliste"}
    }
)
def list_containers():
    """
    Gibt eine Liste aller laufenden Container zurück.
    """
    try:
        return container_service.list_running_containers()
    except Exception as e:
        logger.exception("[ContainerList] Fehler beim Abrufen der Container")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Containerliste")
