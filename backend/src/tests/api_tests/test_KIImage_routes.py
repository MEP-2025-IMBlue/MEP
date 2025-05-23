from fastapi.testclient import TestClient
from backend.src.main import app
from db.database.database import get_db
from tests.api_tests.fixtures import *
from tests.api_tests.utils import *

client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db

def test_get_ki_images_list_empty():
    response = client.get("/ki-images")
    assert response.status_code == 404
    assert response.json() == {"detail": "Es befinden sich noch keine KI-Images in der Datenbank."}