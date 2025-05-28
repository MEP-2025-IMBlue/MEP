import logging
import json
from datetime import datetime
import os

# Verzeichnis für Logdateien (Standard: /tmp/logs, wird von Docker gemountet)
log_verzeichnis = os.getenv("LOG_DIR", "/tmp/logs")
os.makedirs(log_verzeichnis, exist_ok=True)

# Dateiname im Format YYYY-MM-DD.log im LOG_DIR
log_filename = os.path.join(log_verzeichnis, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")

# Konfiguriert den Logger
logger = logging.getLogger("event_logger")
logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR erlauben

# Formatter: JSON-Zeile pro Eintrag
formatter = logging.Formatter('%(message)s')

# Datei-Handler: schreibt in log_filename
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(formatter)

# Konsolen-Handler: schreibt auf stdout
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Verhindert doppelte Handler bei mehrfacher Initialisierung (z. B. Hot Reload)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_event(event_type: str, source: str, message: str, level: str = "ERROR"):
    """
    Protokolliert ein strukturiertes Ereignis im JSON-Format.

    Parameter:
        event_type (str): Kategorie (z. B. "Fehler", "System", "Upload")
        source (str): Ursprungsmodul oder Funktion
        message (str): Beschreibung des Ereignisses
        level (str): Log-Level ("DEBUG", "INFO", "WARNING", "ERROR")

    Ergebnis:
        Der Logeintrag wird als JSON-Zeile in eine Datei im LOG_DIR geschrieben und auf der Konsole ausgegeben.
    """

    log_eintrag = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type.upper(),
        "source": source,
        "message": message
    }

    level = level.upper()
    if level == "DEBUG":
        logger.debug(json.dumps(log_eintrag))
    elif level == "INFO":
        logger.info(json.dumps(log_eintrag))
    elif level == "WARNING":
        logger.warning(json.dumps(log_eintrag))
    else:
        logger.error(json.dumps(log_eintrag))
