from src.api.py_models.py_models import KIImageMetadata
from typing import List

# Simulierte In-Memory-Datenbank
fake_db: List[KIImageMetadata] = []

# ------------------------------------------------------------
# Abschnitt: Exceptions

class KIImageNotFoundError(Exception): pass
class NoKIImagesInTheList(Exception): pass
class InvalidImageIDError(Exception): pass

# ------------------------------------------------------------
# Abschnitt: Funktionen

def get_all_ki_images():
    if len(fake_db) == 0:
        raise NoKIImagesInTheList()
    return fake_db

def get_ki_image_by_id(image_id: int):
    if not image_id:
        raise InvalidImageIDError()
    for ki_image in fake_db:
        if ki_image.image_id == image_id:
            return ki_image
    raise KIImageNotFoundError()

def add_ki_image(ki_image: KIImageMetadata):
    for entry in fake_db:
        if entry.image_id == ki_image.image_id:
            raise ValueError(f"Ein Bild mit der ID {ki_image.image_id} existiert bereits.")
    fake_db.append(ki_image)
    return ki_image

def delete_ki_image(image_id: str):
    for index, ki_image in enumerate(fake_db):
        if ki_image.image_id == image_id:
            return fake_db.pop(index)
    raise KIImageNotFoundError()

# ------------------------------------------------------------
# Abschnitt: Neue Import KI-Image für Lokal und DockerHub Funktion
from src.api.py_models.py_models import KIImageMetadata
import docker
import tempfile, os
from typing import Optional
import logging

logger = logging.getLogger(__name__)
docker_client = docker.from_env()

def import_local_image(file_bytes: bytes) -> dict:
    if not file_bytes:
        raise ValueError("File is required for local import")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name
        logger.info(f"Temp file saved at {temp_file_path}")
    
    with open(temp_file_path, "rb") as f:
        images = docker_client.images.load(f.read())
        imported_image = images[0]

    repo_tags = imported_image.attrs.get("RepoTags", [])
    if repo_tags:
        full_name = repo_tags[0]
        parts = full_name.split(":")
        image_name = parts[0]
        image_tag = parts[1] if len(parts) > 1 else "latest"
    else:
        raise ValueError("Could not determine image name and tag from tar file")
    
    os.unlink(temp_file_path)
    
    image_data = {
        "image_name": image_name,
        "image_tag": image_tag,
        "image_description": None,
        "image_path": None,
        "image_local_name": f"{image_name}:{image_tag}",
        "image_provider_id": 1  # TODO: dynamisch, falls User
    }
    return image_data

def import_hub_repositorie_image(image_reference: str) -> dict:
    if not image_reference:
        raise ValueError("image_reference required for Hub Repository import")
    
    #docker_client.images.pull(f"{image_name}:{image_tag}")
    docker_client.images.pull(f"{image_reference}")

    #Wurde hinzugefügt, da Datenbank noch separat nach Image_Name und Image_Tag frägt
    if ":" in image_reference:
        image_name, image_tag = image_reference.rsplit(":", 1)
    
    image_data = {
        "image_name": image_name,
        "image_tag": image_tag,
        "image_description": None, #Optional
        "image_path": None, #Braucht man nicht mehr
        "image_local_name": f"{image_reference}", #Name ändern in image_reference
        "image_provider_id": 1
    }
    return image_data
