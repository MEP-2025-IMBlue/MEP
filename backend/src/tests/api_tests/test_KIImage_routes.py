from fastapi.testclient import TestClient
from src.main import app
from src.api.py_models import *
from src.api.routes import *
from src.services.image_upload.service_KIImage import fake_db

import os
#from fastapi.testclient import TestClient
#from src.main import app

os.environ["DB_HOST"] = "db"  # Setze die Umgebungsvariablen für die Datenbankverbindung
os.environ["DB_USER"] = "user"
os.environ["DB_PASSWORD"] = "password"

client = TestClient(app)

#client = TestClient(app)

# ------------------------------------------------------------
# Abschnitt: Hilfsfunktionen

def setup_function():
    fake_db.clear()

def add_sample_ki_image():
    response = client.post("/ki-images", json={
        "image_id": 123,
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0",
        "description": "Dies ist ein Test-Image für KI-Zwecke",
        "image_path": "docker.io/user/meine-ki-anwendung",
        "local_image_name": "meine-ki-anwendung:latest",
        "user_id": 42
})
    assert response.status_code == 200
    assert response.json() == {
        "image_id": 123,
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0",
        "description": "Dies ist ein Test-Image für KI-Zwecke",
        "image_path": "docker.io/user/meine-ki-anwendung",
        "local_image_name": "meine-ki-anwendung:latest",
        "user_id": 42
}
    return response

# ------------------------------------------------------------
# Abschnitt: Tests für GET

def test_get_ki_images_list_empty():

    response = client.get("/ki-images")
    assert response.status_code == 404
    assert response.json() == {"detail": "Es befinden sich noch keine KI-Images in der Datenbank."}




def test_get_ki_images_list_after_post():
    add_sample_ki_image()
    response = client.get("/ki-images")
    assert response.status_code == 200 
    assert any(item["image_id"] == 123 for item in response.json())

# ------------------------------------------------------------
# Abschnitt: Tests für POST

def test_post_ki_image_valid_and_duplicate():
    response_first = client.post("/ki-images", json={
        "image_id": 123,
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0",
        "description": "Dies ist ein Test-Image für KI-Zwecke",
        "image_path": "docker.io/user/meine-ki-anwendung",
        "local_image_name": "meine-ki-anwendung:latest",
        "user_id": 42
})
    assert response_first.status_code == 200
    assert response_first.json() == {
        "image_id": 123,
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0",
        "description": "Dies ist ein Test-Image für KI-Zwecke",
        "image_path": "docker.io/user/meine-ki-anwendung",
        "local_image_name": "meine-ki-anwendung:latest",
        "user_id": 42
}

    response_second = client.post("/ki-images", json={
        "image_id": 123,
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0",
        "description": "Dies ist ein Test-Image für KI-Zwecke",
        "image_path": "docker.io/user/meine-ki-anwendung",
        "local_image_name": "meine-ki-anwendung:latest",
        "user_id": 42
})
    assert response_second.status_code == 400
    assert response_second.json() == {"detail": "Ein Bild mit der ID 123 existiert bereits."}

def test_post_ki_image_invalid_fields():
    response = client.post("/ki-images", json={"image_id": 123})
    assert response.status_code == 422  
    assert "detail" in response.json()

def test_post_ki_image_without_optional_fields():
    response = client.post("/ki-images", json={
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0"
})
    assert response.status_code == 200

# ------------------------------------------------------------
# Abschnitt: Tests für DELETE

def test_delete_ki_image():
    add_sample_ki_image()
    response_delete = client.delete("/ki-images/123")
    assert response_delete.status_code == 200

    response_check = client.get("/ki-images")
    assert response_check.status_code == 404

def test_delete_ki_image_invalid_id():
    add_sample_ki_image()
    response = client.delete("/ki-images/345")
    assert response.status_code == 404
    assert response.json() == {"detail": "KI-Image mit der ID 345 wurde nicht gefunden."}

# ------------------------------------------------------------
# Abschnitt: Tests für PUT (noch offen)

# ------------------------------------------------------------
# Abschnitt: Unzugeordnete Tests

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome"}