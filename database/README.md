# 📦 Ordner: `database/`

## Zweck
Dieser Ordner enthält Konfigurationsdateien zur **Initialisierung der Datenbank**, insbesondere für den Einsatz mit Docker-Compose.

## Inhalt

- `.env`: Enthält sensible Informationen wie `DATABASE_URL`, DB-Benutzername und Passwort.
- `schemas/init.sql`: SQL-Skript zur Initialisierung der Tabellenstruktur in der Datenbank. Wird automatisch ausgeführt, wenn ein PostgreSQL-Container startet.

## Hinweise zur Nutzung

- Das `init.sql`-Skript ist besonders sinnvoll beim ersten Starten des Containers oder zum Testen.
- Die Tabellenstruktur in `init.sql` muss **synchron** mit den Modellen in `db_models.py` sein.
- Änderungen an Feldern müssen sowohl hier als auch im Python-Code (SQLAlchemy + Pydantic) erfolgen (Siehe README.md im Backend).
