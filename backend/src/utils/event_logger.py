# event_logger.py
import logging
import json
from datetime import datetime
import os
import sys  # für stdout 

#  Log-Verzeichnis (über Umgebungsvariable oder Standardpfad)
LOG_DIR = os.getenv("LOG_DIR", "logs")
today_str = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOG_DIR, f"{today_str}.log")
os.makedirs(LOG_DIR, exist_ok=True)

# 🛠 Logger-Instanz
logger = logging.getLogger("event_logger")
logger.setLevel(logging.DEBUG)  # Unterstützt: DEBUG, INFO, WARNING, ERROR

#  Formatter für strukturierte JSON-Logs
def json_formatter(record):
    base = {
        "timestamp": datetime.fromtimestamp(record.created).isoformat(),
        "level": record.levelname,
        "source": getattr(record, "source", None),
        "action": getattr(record, "action", None),
        "message": record.getMessage(),
        "user_id": getattr(record, "user_id", None),
        "container_id": getattr(record, "container_id", None),
        "container_name": getattr(record, "container_name", None),
        "image_id": getattr(record, "image_id", None),
        "cpu": getattr(record, "cpu", None),
        "ram": getattr(record, "ram", None),
    }
    return json.dumps({k: v for k, v in base.items() if v is not None})

#  Benutzerdefinierter Formatter (JSON)
class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        return json_formatter(record)

#  File-Handler (schreibt Logs in Datei)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(JSONLogFormatter())
logger.addHandler(file_handler)

#  Stream-Handler (für stdout-Ausgabe)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(JSONLogFormatter())
logger.addHandler(stream_handler)

#  Hauptfunktion zum strukturierten Loggen eines Ereignisses
# Unterstützt Level: DEBUG, INFO, WARNING, ERROR
def log_event(source: str, action: str, message: str, level: str = "INFO",
              container_id=None, container_name=None, image_id=None,
              cpu=None, ram=None, user_id=None):
    extra = {
        "source": source,
        "action": action,
        "container_id": container_id,
        "container_name": container_name,
        "image_id": image_id,
        "cpu": cpu,
        "ram": ram,
        "user_id": user_id
    }

    if level == "DEBUG":
        logger.debug(message, extra=extra)
    elif level == "INFO":
        logger.info(message, extra=extra)
    elif level == "WARNING":
        logger.warning(message, extra=extra)
    elif level == "ERROR":
        logger.error(message, extra=extra)
    else:
        logger.info(message, extra=extra)
