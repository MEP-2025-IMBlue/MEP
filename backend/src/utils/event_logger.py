import logging
import json
from datetime import datetime
import os
import sys  # für stdout 

# Log-Verzeichnis aus Umgebungsvariable oder Standardwert
LOG_DIR = os.getenv("LOG_DIR", "logs")
#Automatisch tägliche Log-Dateien erstellen
today_str = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOG_DIR, f"{today_str}.log")
#LOG_FILE = os.path.join(LOG_DIR, "events.log") #events.log 
os.makedirs(LOG_DIR, exist_ok=True)

# Logger konfigurieren
logger = logging.getLogger("event_logger")
logger.setLevel(logging.DEBUG)  # Unterstützt DEBUG, INFO, WARNING, ERROR

# --- Formatter für strukturierte JSON-Logs ---
def json_formatter(record):
    base = {
        "timestamp": datetime.fromtimestamp(record.created).isoformat(),
        "level": record.levelname,
        "source": getattr(record, "source", None),
        "action": getattr(record, "action", None),
        "message": record.getMessage()
    }

    # Diese optionalen Felder werden nur hinzugefügt, wenn sie vorhanden sind
    for attr in ["container_id", "cpu", "ram", "user_id"]:
        value = getattr(record, attr, None)
        if value is not None:
             base[attr] = value

    return json.dumps(base)

# Benutzerdefinierter Formatter mit JSON-Ausgabe
class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        return json_formatter(record)

# --- File Handler: schreibt Logs in Datei ---
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(JSONLogFormatter())
logger.addHandler(file_handler)

# --- Stream Handler: schreibt Logs in stdout (Konsole) ---
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(JSONLogFormatter())
logger.addHandler(stream_handler)

# Funktion zum Loggen eines strukturierten Ereignisses
# Unterstützt die Level: DEBUG, INFO, WARNING, ERROR
def log_event(source: str, action: str, message: str, level: str = "INFO", container_id=None, cpu=None, ram=None, user_id=None):
    extra = {
        "source": source,
        "action": action,
        "container_id": container_id,
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