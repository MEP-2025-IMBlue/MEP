# 📦 Ordner: `src/api/`

## Zweck
Dieses Modul enthält die **REST-API-Endpunkte** und alle zugehörigen **Pydantic-Modelle** für die FastAPI-Anwendung.

## Inhalt

- `routes/`: Hier liegen alle FastAPI-Endpunkt-Definitionen – z. B. `dicom_routes.py`, `kiImage_routes.py`.
- `py_models/`: Hier befinden sich die Pydantic-Datenmodelle für Ein- und Ausgaben der API.

## Nutzung
- Jedes Modul (`dicom`, `kiImage`, `container`) hat üblicherweise eigene Routen und Modelle.
- Änderungen an Tabellenspalten müssen in den Pydantic-Modellen (`py_models.py`) angepasst werden.
- Die API spricht über `Depends(get_db)` mit der Datenbank.
