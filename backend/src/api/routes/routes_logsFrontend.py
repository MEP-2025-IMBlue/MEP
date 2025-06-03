from fastapi import APIRouter, Request
from src.utils.event_logger import log_event
from pydantic import BaseModel

# Router für Frontend-Log-Ereignisse
router = APIRouter()

# Schema für eingehende Logdaten
class FrontendLog(BaseModel):
    source: str = "frontend"
    action: str
    message: str
    level: str = "INFO"

# Endpoint zum Empfangen von Logs aus dem Frontend
@router.post("/frontend-log")
async def receive_frontend_log(log: FrontendLog, request: Request):
    client_ip = request.client.host
    source = f"{log.source}:{client_ip}"  # z.B. "container_logs.js:127.0.0.1"
    log_event(source=source, action=log.action, message=log.message, level=log.level)
    return {"status": "ok"}
