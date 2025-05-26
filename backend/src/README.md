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
