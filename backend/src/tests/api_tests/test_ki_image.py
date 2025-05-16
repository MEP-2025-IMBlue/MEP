# backend/src/tests/api_tests/test_ki_image.py
import io
import pytest
from unittest.mock import patch
from fastapi import status

# ===== Test: Lokales KI-Image hochladen (.tar Datei) =====
@patch("api.routes.routes_KiImage.service_KIImage.import_local_image")
@patch("api.routes.routes_KiImage.crud_kiImage.create_ki_image")
def test_upload_local_ki_image_success(mock_create_image, mock_import_image, client):
    fake_metadata = {
        "id": "test-id",
        "name": "test-image",
        "tag": "latest"
    }
    mock_import_image.return_value = fake_metadata
    mock_create_image.return_value = fake_metadata

    tar_file = io.BytesIO(b"fake docker tar data")
    tar_file.name = "image.tar"

    response = client.post(
        "/ki-images/local",
        files={"file": ("image.tar", tar_file, "application/x-tar")},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "test-image"
    assert mock_import_image.called
    assert mock_create_image.called

# ===== Test: KI-Image von DockerHub laden =====
@patch("api.routes.routes_KiImage.service_KIImage.import_hub_repositorie_image")
@patch("api.routes.routes_KiImage.crud_kiImage.create_ki_image")
def test_pull_ki_image_success(mock_create_image, mock_import_image, client):
    fake_metadata = {
        "id": "test-id",
        "name": "hub-image",
        "tag": "latest"
    }
    mock_import_image.return_value = fake_metadata
    mock_create_image.return_value = fake_metadata

    response = client.post(
        "/ki-images/hub",
        data={"image_reference": "hub/image:latest"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "hub-image"
    assert mock_import_image.called
    assert mock_create_image.called
