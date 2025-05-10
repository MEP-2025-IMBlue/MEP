import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.db.database.database import get_db
from src.db.db_models import db_models  # Dein ORM-Modell für die DB

# Setze Umgebungsvariablen für Test-Datenbankverbindung
os.environ["DB_HOST"] = "db"  # Docker-Containername für die DB
os.environ["DB_USER"] = "imblue_user"
os.environ["DB_PASSWORD"] = "secret"
os.environ["DB_NAME"] = "imblue_db"
os.environ["DB_PORT"] = "5432"

# Erstelle die DATABASE_URL aus den Umgebungsvariablen
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Erstelle die Engine und die Session für SQLAlchemy
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Datenbank neu initialisieren für jeden Testlauf
@pytest.fixture(scope="function", autouse=True)
def reset_database():
    db_models.Base.metadata.drop_all(bind=engine)  # Löscht alle Tabellen
    db_models.Base.metadata.create_all(bind=engine)  # Erstellt die Tabellen neu
    yield  # Tests laufen hier
    db_models.Base.metadata.drop_all(bind=engine)  # Löscht alle Tabellen nach jedem Test

# Dependency-Override für die Datenbankverbindung
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Testclient für die FastAPI-Anwendung
client = TestClient(app)

def add_sample_ki_image():
    """
    Hilfsfunktion, um ein Beispiel-KI-Image in die DB hinzuzufügen.
    """
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
    """
    Test für den Fall, dass keine KI-Images in der Datenbank sind.
    """
    response = client.get("/ki-images")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Es befinden sich noch keine KI-Images in der Datenbank."
    }

def test_get_ki_images_list_after_post():
    """
    Test, ob die KI-Images nach dem POST hinzugefügt werden.
    """
    add_sample_ki_image()  # Ein KI-Image hinzufügen
    response = client.get("/ki-images")
    assert response.status_code == 200
    assert any(item["image_id"] == 123 for item in response.json())

# ------------------------------------------------------------
# Abschnitt: Tests für POST

def test_post_ki_image_valid_and_duplicate():
    """
    Test, um ein KI-Image hinzuzufügen und Duplikate zu überprüfen.
    """
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
    assert response_second.json() == {
        "detail": "Ein Bild mit der ID 123 existiert bereits."
    }

def test_post_ki_image_invalid_fields():
    """
    Test für den Fall von ungültigen Feldern beim POST.
    """
    response = client.post("/ki-images", json={"image_id": 123})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_post_ki_image_without_optional_fields():
    """
    Test, um sicherzustellen, dass auch bei fehlenden optionalen Feldern keine Fehler auftreten.
    """
    response = client.post("/ki-images", json={
        "image_name": "meine-ki-anwendung",
        "image_tag": "v1.0"
    })
    assert response.status_code == 200

# ------------------------------------------------------------
# Abschnitt: Tests für DELETE

def test_delete_ki_image():
    """
    Test zum Löschen eines KI-Images.
    """
    add_sample_ki_image()  # Ein KI-Image hinzufügen
    response_delete = client.delete("/ki-images/123")
    assert response_delete.status_code == 200

    response_check = client.get("/ki-images")
    assert response_check.status_code == 404

def test_delete_ki_image_invalid_id():
    """
    Test zum Löschen eines KI-Images mit einer ungültigen ID.
    """
    add_sample_ki_image()  # Ein KI-Image hinzufügen
    response = client.delete("/ki-images/345")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "KI-Image mit der ID 345 wurde nicht gefunden."
    }

# ------------------------------------------------------------
# Abschnitt: Unzugeordnete Tests

def test_home():
    """
    Einfacher Test für den Home-Endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome"}
