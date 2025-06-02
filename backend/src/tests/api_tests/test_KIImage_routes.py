from src.main import app
from src.db.database.database import get_db
from src.tests.api_tests.utils import override_get_db
from src.tests.api_tests.fixtures import *
from fastapi.testclient import TestClient

client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db

def test_get_ki_images():
    response = client.get("/ki-images")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_ki_image_by_id():
    response = client.get("/ki-images/300")
    assert response.status_code == 200
    data = response.json()
    assert data["image_id"] == 300

def test_get_ki_image_by_wrong_id():
    response = client.get("/ki-images/3")
    assert response.status_code == 404

def test_post_ki_image_from_hub():
    response = client.post("/ki-images/hub", data={"image_reference": "hello-world:latest"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["image_id"], int)
    assert data["image_name"] == "hello-world"
    assert data["image_tag"] == "latest"
    assert "image_created_at" in data


