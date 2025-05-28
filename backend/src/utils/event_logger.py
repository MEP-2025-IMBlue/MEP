import logging
import json
from datetime import datetime
import os

# Erstellt automatisch das Verzeichnis "logs", falls es nicht existiert
os.makedirs("logs", exist_ok=True)

# Benennt die Logdatei nach dem aktuellen UTC-Datum (z. B. logs/2025-05-28.log)
log_filename = f"logs/{datetime.utcnow().strftime('%Y-%m-%d')}.log"

# Konfiguriert den Logger für strukturierte JSON-Ausgaben
logger = logging.getLogger("event_logger")
logger.setLevel(logging.DEBUG)  # DEBUG dahil tüm seviyeleri göster

# Formatter: Reine JSON-Zeile pro Eintrag
formatter = logging.Formatter('%(message)s')

# FileHandler: Log-Datei
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(formatter)

# StreamHandler: Konsole (stdout)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Handler nur einmal hinzufügen (z. B. bei Hot Reload vermeiden)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_event(event_type: str, source: str, message: str, level: str = "ERROR"):
    """
    Protokolliert ein strukturiertes Ereignis mit Zeitstempel, Typ, Quelle und Nachricht.

    Parameter:
        event_type (str): Kategorie des Ereignisses (z. B. "Fehler", "System", "Aktion")
        source (str): Ursprungsmodul oder Funktion
        message (str): Beschreibende Nachricht
        level (str): Log-Level ("DEBUG", "INFO", "WARNING", "ERROR")

    Ausgabe:
        JSON-formatierte Logzeile in einer Datei im logs/-Verzeichnis und in der Konsole
    """

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type.upper(),
        "source": source,
        "message": message
    }

    level = level.upper()
    if level == "DEBUG":
        logger.debug(json.dumps(log_entry))
    elif level == "INFO":
        logger.info(json.dumps(log_entry))
    elif level == "WARNING":
        logger.warning(json.dumps(log_entry))
    else:
        logger.error(json.dumps(log_entry))
