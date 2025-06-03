from fastapi import APIRouter, Request, HTTPException
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
async def receive_frontend_log(request: Request):
    try:
        data = await request.json()
        log_event(
            source="FRONTEND",
            action=data.get("action", "Unknown"),
            message=data.get("message", ""),
            level=data.get("level", "INFO")
        )
        return {"message": "Frontend-Log received"}
    except Exception as e:
        log_event("ERROR", "receive_frontend_log", f"Fehler beim Empfangen des Frontend-Logs: {str(e)}", level="ERROR")
        raise HTTPException(status_code=500, detail="Fehler beim Verarbeiten des Frontend-Logs")
    
@router.get("/logs/events")
async def get_logs(limit: int = 10):
    log_path = "storage/logs/events.log"
    if not os.path.exists(log_path):
        return JSONResponse(status_code=404, content={"detail": "Logdatei nicht gefunden."})

    with open(log_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    last_lines = lines[-limit:] if len(lines) > limit else lines
    return {"logs": last_lines[::-1]}    