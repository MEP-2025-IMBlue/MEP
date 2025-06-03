import sys
import os

# Projektpfad zum Importieren von Modulen aus übergeordnetem Verzeichnis setzen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.db_models.db_models import Base
from src.db.database.database import get_db

# -------------------------------------------------------
# Pytest-Fixture für einen isolierten FastAPI-Testclient 
# mit einer In-Memory-SQLite-Datenbank.
@pytest.fixture(scope="function")
def test_client():
    # Temporäre SQLite-Datenbank im Speicher (für Unit-Tests)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Datenbanktabellen gemäß Base-Klassenmodell erstellen
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Dependency Injection: Ersetze die originale DB-Verbindung durch unsere Testverbindung
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # TestClient an Tests übergeben
    yield client

    # Aufräumen nach dem Test: Overrides und Tabellen löschen
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

# -------------------------------------------------------
# Hilfsfunktion: Beispiel-KI-Image über POST-Request anlegen
def add_sample_ki_image(client):
    response = client.post("/ki-images/hub", data={
        "image_reference": "ubuntu:latest"
    })
    assert response.status_code == 200
    return response.json()

# -------------------------------------------------------
# GET-Tests: KI-Images abfragen

def test_get_ki_images_list_empty(test_client):
    """
    Test: Leere Liste abfragen → Erwartung: 404 mit Fehlermeldung.
    """
    response = test_client.get("/ki-images")
    assert response.status_code == 404
    assert "keine ki-bilder in der datenbank" in response.json()["detail"].lower()

def test_get_ki_images_list_after_post(test_client):
    """
    Test: Nach erfolgreichem POST sollte GET eine Liste mit einem Eintrag liefern.
    """
    add_sample_ki_image(test_client)
    response = test_client.get("/ki-images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1

# -------------------------------------------------------
# POST-Tests: KI-Image registrieren

def test_post_ki_image_valid_and_duplicate(test_client):
    """
    Test: Zwei identische POST-Requests (Duplikate) sind erlaubt und führen zu 200 OK.
    """
    data = {"image_reference": "ubuntu:latest"}

    response1 = test_client.post("/ki-images/hub", data=data)
    assert response1.status_code == 200
    assert response1.json()["image_reference"] == "ubuntu:latest"

    response2 = test_client.post("/ki-images/hub", data=data)
    assert response2.status_code == 200
    assert response2.json()["image_reference"] == "ubuntu:latest"

def test_post_ki_image_invalid_missing_fields(test_client):
    """
    Test: POST ohne 'image_reference' sollte mit 422 (Unprocessable Entity) fehlschlagen.
    """
    response = test_client.post("/ki-images/hub", data={})
    assert response.status_code == 422  # Fehlende Pflichtfelder

# -------------------------------------------------------
# DELETE-Tests: KI-Image löschen

def test_delete_ki_image_success(test_client):
    """
    Test: KI-Image erfolgreich löschen und prüfen, ob es danach nicht mehr in der Liste erscheint.
    """
    image = add_sample_ki_image(test_client)
    image_id = image["image_id"]

    response = test_client.delete(f"/ki-images/{image_id}")
    assert response.status_code == 200
    assert f"{image_id}" in response.json()["message"]

    # Überprüfen, ob das Bild wirklich gelöscht wurde
    response_check = test_client.get("/ki-images")
    assert response_check.status_code == 404

def test_delete_ki_image_not_found(test_client):
    """
    Test: Löschen eines nicht vorhandenen KI-Images → Erwartung: 404-Fehler.
    """
    response = test_client.delete("/ki-images/99999")
    assert response.status_code == 404
    assert "nicht gefunden" in response.json()["detail"].lower()

# -------------------------------------------------------
# Basis-Endpunkt ("/") testen

def test_home(test_client):
    """
    Test: Startseite aufrufen → Begrüßungsnachricht prüfen.
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to mRay AIR Backend!"}
