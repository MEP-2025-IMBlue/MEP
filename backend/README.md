🛠️ Welche Dateien musst du anpassen, wenn die Tabellenspalten geändert werden?


Bereich	                |        Betroffene Datei(n)	         |                  Warum?
--------------------------------------------------------------------------------------------------------------------
SQLAlchemy-Modelle	    |           db_models.py	             | Hier definierst du die Tabellenstruktur in Python
SQL-Schema (init.sql)	|    database/schemas/init.sql	         |  Falls du DB auch über SQL initialisierst 
Pydantic-Modelle	    |           py_models.py	             |  Für FastAPI: Input-/Output-Validierung
CRUD-Funktionen	        |   crud_dicom.py, crud_kiImage.py, etc. |	   Wenn du neue Felder lesen/schreiben willst
Optional: Services	    |            services/...	             |  Falls du Datenlogik mit neuen Feldern ergänzt
Optional: Tests	        |              tests/...	             |  Wenn du Tests auf Felder/Antworten prüfst