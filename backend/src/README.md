# 📦 Ordner: `src/`

## Zweck
Enthält alle Hauptkomponenten des Backends der Anwendung – sauber modularisiert nach Funktion.

## Inhalt

- `api/`: Endpunkte (FastAPI-Routen) und Input-/Output-Modelle (Pydantic)
- `db/`: Datenbankmodelle (SQLAlchemy), Datenbankverbindung, CRUD-Funktionen, Tests
- `crud/`: Wird als Untermodul von `db` genutzt
- `database/`: Technische Anbindung an SQL-Datenbank
- `services/`: Platz für spätere Business-Logik oder komplexe Funktionen
- `tests/`: Testskripte für Routen, Logik und Datenbank
- `main.py`: Einstiegspunkt der FastAPI-Anwendung

## Start
Die Anwendung wird über `main.py` gestartet. Von dort aus wird das API-Routing geladen.

## Hinweis
Beim Ändern von Datenbankfeldern immer die Abhängigkeiten in `api`, `db_models`, `init.sql`, `crud` und `py_models` synchron halten.

## Logging-System

Das Logging-System der Backend-Anwendung ist zentral im Modul `event_logger.py` implementiert und unterstützt strukturierte, JSON-basierte Logeinträge.

### Speicherort

Alle Logs werden im Verzeichnis `storage/logs/` gespeichert. Abhängig von der Konfiguration gibt es zwei Varianten:

- **Standardmodus**: Alle Logeinträge werden in einer Datei `events.log` gesammelt.
- **Tägliche Logrotation (empfohlen)**: Die Logdateien werden automatisch nach Datum benannt (Format: `YYYY-MM-DD.log`, z. B. `2025-06-03.log`).

### Logformat

Die Logeinträge sind als JSON strukturiert und enthalten folgende Felder:

| Feld        | Beschreibung                                     |
|-------------|--------------------------------------------------|
| `timestamp` | Zeitstempel des Ereignisses (ISO-Format)         |
| `level`     | Log-Level (DEBUG, INFO, WARNING, ERROR)          |
| `source`    | Herkunft des Logs (z. B. CONTAINER, API, etc.)    |
| `action`    | Ausgeführte Aktion (z. B. start_container)        |
| `message`   | Beschreibung der Aktion oder des Fehlers         |
| `optional`  | Zusätzliche Felder wie `container_id`, `cpu`, `ram`, `user_id` bei Bedarf |

### ⚙️ Anwendung im Code

Logging erfolgt zentral über die Funktion `log_event()`:

```python
from event_logger import log_event

log_event(
    source="CONTAINER",
    action="start_container",
    message="Container erfolgreich gestartet",
    level="INFO",
    container_id="mep-backend"
)

