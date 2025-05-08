# 📦 Ordner: `src/db/`

## Zweck
Dieses Modul enthält alle Komponenten zur **Datenbankanbindung und Datenbanklogik** in SQLAlchemy.

## Inhalt

- `db_models/`: Enthält die Tabellenmodelle (`db_models.py`) basierend auf SQLAlchemy.
- `crud/`: Enthält CRUD-Funktionen (Create, Read, Update, Delete) für jede Entität wie `dicom`, `kiImage`, `container`.
- `database/`: Stellt die Verbindung zur Datenbank her und verwaltet SQLAlchemy Sessions (`database.py`).
- `core/`: Enthält zentrale Ausnahmen oder Konfigurationen wie `exceptions.py`.
- `tests/`: Tests für die Datenbankfunktionen usw.
- `services/`: Optional für business logic; noch keine detaillierte Implementierung.

## Nutzung
- Alle Datenbankzugriffe im Backend laufen über diese Struktur.
- Die Modelle in `db_models` werden auch für automatische Tabellenerstellung verwendet.
- `crud_*`-Dateien sollten aktualisiert werden, wenn sich die Struktur ändert.
