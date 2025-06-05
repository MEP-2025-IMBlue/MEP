from fastapi import APIRouter, Request, HTTPException, Query
from src.utils.event_logger import log_event
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import os
import json

# Router für Frontend-Log-Ereignisse
router = APIRouter()

# Datenmodell für eingehende Logdaten aus dem Frontend
class FrontendLog(BaseModel):
    source: str = "frontend"     # Herkunft des Logs (z. B. "frontend")
    action: str                  # Aktion, die geloggt wird
    message: str                 # Beschreibung der Aktion oder Meldung
    level: str = "INFO"          # Log-Level: INFO, WARNING, ERROR, etc.

# Endpoint zum Empfangen und Speichern von Frontend-Logs
@router.post("/frontend-log")
async def receive_frontend_log(request: Request):
    try:
        # JSON-Daten aus der Anfrage extrahieren
        data = await request.json()
        
        # Log-Ereignis strukturiert erfassen
        log_event(
            source="FRONTEND",
            action=data.get("action", "Unknown"),
            message=data.get("message", ""),
            level=data.get("level", "INFO")
        )
        return {"message": "Frontend-Log empfangen"}
    
    except Exception as e:
        # Fehler beim Verarbeiten des Logs erfassen
        log_event(
            source="ERROR",
            action="receive_frontend_log",
            message=f"Fehler beim Empfangen des Frontend-Logs: {str(e)}",
            level="ERROR"
        )
        raise HTTPException(status_code=500, detail="Fehler beim Verarbeiten des Frontend-Logs")

# Endpoint zum Abrufen der Log-Einträge eines bestimmten Tages (oder vom aktuellen Tag)
@router.get("/logs/events")
async def get_logs(
    limit: int = 10,
    date: str = Query(default=None),
    level: str = Query(default=None),
    source: str = Query(default=None),
    action: str = Query(default=None)
):
    try:
        # Aktuelles Datum oder benutzerdefiniertes
        if date:
            datetime.strptime(date, "%Y-%m-%d")
            log_path = f"logs/{date}.log"
        else:
            today_str = datetime.now().strftime("%Y-%m-%d")
            log_path = f"logs/{today_str}.log"

        if not os.path.exists(log_path):
            return JSONResponse(status_code=404, content={"detail": "Logdatei nicht gefunden."})

        parsed_logs = []

        with open(log_path, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    log_entry = json.loads(line)

                    # Filter anwenden, wenn gesetzt
                    if level and log_entry.get("level", "").upper() != level.upper():
                        continue
                    if source and log_entry.get("source", "").lower() != source.lower():
                        continue
                    if action and action.lower() not in log_entry.get("action", "").lower():
                        continue

                    parsed_logs.append(log_entry)

                except json.JSONDecodeError:
                    continue

        # Nach Zeit sortieren und limitieren
        parsed_logs.sort(key=lambda log: datetime.fromisoformat(log["timestamp"]))
        return {"logs": parsed_logs[-limit:]}

    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Ungültiges Datumsformat. Erwartet: YYYY-MM-DD"}
        )