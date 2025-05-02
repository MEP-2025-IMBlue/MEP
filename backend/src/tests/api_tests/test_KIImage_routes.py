from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.api.py_models import *
from backend.src.api.routes import *
from backend.src.services.image_upload.service_KIImage import fake_db

client = TestClient(app)

# Abschnitt 1: Hilfsfunktionen
# ------------------------------------------------------------

def setup_function():
    fake_db.clear()

def add_sample_ki_image():
    response = client.post("/add-KIimage", json={
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

# Abschnitt 2: Tests für GET
# ------------------------------------------------------------

def test_get_list_KIimages():
    response_first = client.get("/list-KIimages")
    assert response_first.status_code == 404
    assert response_first.json() == {"detail":"Es befinden sich noch keine KI-Images in der Datenbank."}

def test_get_list_KIimages_after_post():
    add_sample_ki_image()
    response_second = client.get("/list-KIimages")
    assert response_second.status_code == 200 
    assert any(item["image_id"] == "string" for item in response_second.json())  # Bild mit der ID 'string' sollte in der Liste sein

# Abschnitt 3: Tests für POST
# ------------------------------------------------------------

def test_post_KIimage1():
    response_first = client.post("/add-KIimage", json={
        "image_id": "string",
        "image_name": "string",
        "tag": "string",
        "repository": "path",
        "created_at": "2025-04-15T",
        "size": 16,
        "architecture": None, # korrekte Verarbeitung von optionalen Feldern
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
    response_second = client.post("/add-KIimage", json={
        "image_id": "string",  # dieselbe ID wie im ersten Test
        "image_name": "string", 
        "tag": "string", 
        "repository": "path", 
        "created_at": "2025-04-15T", 
        "size": 16, 
        "architecture": None, 
        "os": "linux"
    })
    assert response_second.status_code == 400  # Statuscode 400 für Konflikt mit existierender ID
    assert response_second.json() == {"detail": "Ein Bild mit der ID string existiert bereits."}
    
def test_post_KIimage2():
    response = client.post("/add-KIimage", json={"image_id": 123}) #Weitere Eingaben fehlen + image_id erfordert einen String
    assert response.status_code == 422  
    assert "detail" in response.json()  
                        
def test_post_KIimage3():
    response = client.post("/add-KIimage", json={
        "image_id": "string",
        "image_name": "string",
        "tag": "string",
        "repository": "path",
        "created_at": "2025-04-15T",
        "size": 16,
        "architecture": "invalid architecture", # korrekte Verarbeitung von ungültigen Literal Variablen (nur linux, windows erlaubt)
    })
    assert response.status_code == 422
    assert "detail" in response.json()

# Abschnitt 4: Tests für DELETE
# ------------------------------------------------------------

def test_delete_KIimage():
    add_sample_ki_image()
    response_first = client.delete("/delete-KIimage/string")
    assert response_first.status_code == 200

    response_second = client.get("/list-KIimages") #Vergewisserung, dass jetzt die DB leer ist
    assert response_second.status_code == 404

def test_delete_KIimage_wrong_id():
    add_sample_ki_image() # Objekt hinzufügen
    response = client.delete("/delete-KIimage/wrong_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "KI-Image mit der ID wrong_id wurde nicht gefunden."}
    assert any(item.image_id == "string" for item in fake_db)

# Abschnitt 5: Tests für PUT
# ------------------------------------------------------------

# Abschnitt 6: Unzugeordnete Tests
# ------------------------------------------------------------

def test_home () :
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"Welcome"}