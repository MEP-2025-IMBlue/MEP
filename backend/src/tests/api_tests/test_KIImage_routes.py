from fastapi.testclient import TestClient
from src.main import app
from backend.src.api.py_models.py_models import *
from src.api.routes import *
from src.services.image_upload.service_KIImage import fake_db

client = TestClient(app)

# ------------------------------------------------------------
# Abschnitt: Hilfsfunktionen

def setup_function():
    fake_db.clear()

def add_sample_ki_image():
    response = client.post("/ki-images", json={
        "image_id": "string",
        "image_name": "string",
        "tag": "string",
        "repository": "path",
        "created_at": "2025-04-15T",
        "size": 16,
        "architecture": None,
        "os": "linux"
    })
    assert response.status_code == 200
    assert response.json() == {
        "image_id": "string", 
        "image_name": "string", 
        "tag": "string", 
        "repository": "path", 
        "created_at": "2025-04-15T", 
        "size": 16, 
        "architecture": None, 
        "os": "linux"
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
    assert any(item["image_id"] == "string" for item in response.json())

# ------------------------------------------------------------
# Abschnitt: Tests für POST

def test_post_ki_image_valid_and_duplicate():
    response_first = client.post("/ki-images", json={
        "image_id": "string",
        "image_name": "string",
        "tag": "string",
        "repository": "path",
        "created_at": "2025-04-15T",
        "size": 16,
        "architecture": None
    })
    assert response_first.status_code == 200
    assert response_first.json() == {
        "image_id": "string", 
        "image_name": "string", 
        "tag": "string", 
        "repository": "path", 
        "created_at": "2025-04-15T", 
        "size": 16, 
        "architecture": None, 
        "os": None
    }

    response_second = client.post("/ki-images", json={
        "image_id": "string",
        "image_name": "string", 
        "tag": "string", 
        "repository": "path", 
        "created_at": "2025-04-15T", 
        "size": 16, 
        "architecture": None, 
        "os": "linux"
    })
    assert response_second.status_code == 400
    assert response_second.json() == {"detail": "Ein Bild mit der ID string existiert bereits."}

def test_post_ki_image_invalid_fields():
    response = client.post("/ki-images", json={"image_id": 123})
    assert response.status_code == 422  
    assert "detail" in response.json()

def test_post_ki_image_invalid_enum():
    response = client.post("/ki-images", json={
        "image_id": "string",
        "image_name": "string",
        "tag": "string",
        "repository": "path",
        "created_at": "2025-04-15T",
        "size": 16,
        "architecture": "invalid architecture"
    })
    assert response.status_code == 422
    assert "detail" in response.json()

# ------------------------------------------------------------
# Abschnitt: Tests für DELETE

def test_delete_ki_image():
    add_sample_ki_image()
    response_delete = client.delete("/ki-images/string")
    assert response_delete.status_code == 200

    response_check = client.get("/ki-images")
    assert response_check.status_code == 404

def test_delete_ki_image_invalid_id():
    add_sample_ki_image()
    response = client.delete("/ki-images/wrong_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "KI-Image mit der ID wrong_id wurde nicht gefunden."}
    assert any(item.image_id == "string" for item in fake_db)

# ------------------------------------------------------------
# Abschnitt: Tests für PUT (noch offen)

# ------------------------------------------------------------
# Abschnitt: Unzugeordnete Tests

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome"}
