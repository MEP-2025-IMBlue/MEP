# 🧪 Ordner: `src/tests/`

## Zweck
Dieser Ordner enthält **alle automatisierten Tests** für das Backend-System.

## Inhalt & Struktur
- Tests für Routen, Datenbankzugriffe (CRUD), Services und Modelle
- Typischerweise aufgebaut mit `pytest`
- Testdatenbanken oder Mock-Abfragen können hier definiert werden

## Empfehlung
- Für jede Komponente (`api`, `db`, `services`) sollten eigene Testdateien vorhanden sein.
- Testnamen und -fälle sollten klar beschreiben, **was getestet wird** und **was erwartet wird**.
- Testdaten sollten realistische Anwendungsfälle abbilden.

## Starten der Tests
```bash
pytest src/tests/
