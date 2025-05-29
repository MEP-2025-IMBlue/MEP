from src.api.py_models.py_models import KIImageMetadata
from src.utils.event_logger import log_event 
import docker
import tempfile, os
import logging

# ------------------------------------------------------------
# Abschnitt: Funktionen

logger = logging.getLogger(__name__)
docker_client = docker.from_env()

def import_local_image(file_bytes: bytes) -> dict:
    if not file_bytes:
        raise ValueError("File is required for local import")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name
        logger.info(f"Temp file saved at {temp_file_path}")
    try:
        with open(temp_file_path, "rb") as f:
            images = docker_client.images.load(f.read())
            imported_image = images[0]
    except Exception as e:
        # Fehlerlog in zentrale Datei + Konsole
        log_event("KI_IMAGE", "load_failed", str(e), "ERROR")
        raise  # Fehler erneut werfen für FastAPI

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
        "image_reference": f"{image_name}:{image_tag}",
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
        "image_description": None, 
        "image_reference": f"{image_reference}",
        "image_provider_id": 1
    }
    return image_data
