import logging
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..schemas.image import DockerImageBase, ImageUpload
from typing import List
import docker
import os
import tempfile

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["images"])

# Simulierte In-Memory-Datenbank
fake_db = []
docker_client = docker.from_env()

@router.post("/upload", response_model=DockerImageBase) #Upload Image from Docker Hub
async def upload_image(image: DockerImageBase):
    db_image = {
        "id": len(fake_db) + 1,
        "name": image.name,
        "image_tag": image.image_tag,
        "description": image.description,
        "image_path": image.image_path,
        "local_image_name": image.local_image_name,
        "user_id": image.user_id
    }
    fake_db.append(db_image)
    return db_image

@router.post("/upload-local", response_model=DockerImageBase) #Upload Image local
async def upload_local_image(image_data: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith(".tar"):
        logger.error(f"Invalid file extension: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .tar files are allowed")
    
    try:
        logger.info(f"Processing upload for file: {file.filename}")
        # Überprüfe, ob image_data leer oder ungültig ist
        if not image_data or image_data.strip() == "":
            logger.error("image_data is empty or whitespace")
            raise HTTPException(status_code=422, detail="image_data cannot be empty")

        # Parse image_data from string to dict
        try:
            image_data_dict = json.loads(image_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in image_data: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Invalid JSON in image_data: {str(e)}")
        
        # Validiere mit Pydantic
        image_data_model = ImageUpload(**image_data_dict)
        logger.info(f"Validated image_data: {image_data_model.dict()}")

        # Temporäre Datei für die hochgeladene .tar-Datei
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as temp_file:
            content = await file.read()
            logger.info(f"Read {len(content)} bytes from uploaded file")
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Temporary file created at: {temp_file_path}")

        # Importiere das Image mit docker-py
        local_image_name = f"{image_data_model.name}:{image_data_model.image_tag}"
        logger.info(f"Importing image as: {local_image_name}")
        with open(temp_file_path, "rb") as f:
            images = docker_client.images.load(f.read())
            # Benenne das importierte Image um
            imported_image = images[0]  # Erstes Image aus der Liste
            imported_image.tag(local_image_name)
            logger.info(f"Tagged image as: {local_image_name}")

        # Speichere Metadaten in fake_db
        db_image = {
            "id": len(fake_db) + 1,
            "name": image_data_model.name,
            "image_tag": image_data_model.image_tag,
            "description": image_data_model.description,
            "image_path": None,
            "local_image_name": local_image_name,
            "user_id": image_data_model.user_id
        }
        fake_db.append(db_image)
        logger.info(f"Image metadata saved: {db_image}")

        # Entferne temporäre Datei
        os.unlink(temp_file_path)
        logger.info(f"Temporary file deleted: {temp_file_path}")
        return db_image
    except docker.errors.APIError as e:
        logger.error(f"Docker API error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to import image: {str(e)}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/", response_model=List[DockerImageBase])
async def list_images():
    return fake_db

@router.get("/{id}", response_model=DockerImageBase)
async def get_image(id: int):
    for image in fake_db:
        if image["id"] == id:
            return image
    raise HTTPException(status_code=404, detail="Image not found")

@router.put("/{id}", response_model=DockerImageBase)
async def update_image(id: int, image: DockerImageBase):
    for idx, db_image in enumerate(fake_db):
        if db_image["id"] == id:
            updated_image = {
                "id": id,
                "name": image.name,
                "image_tag": image.image_tag,
                "description": image.description,
                "image_path": image.image_path,
                "local_image_name": image.local_image_name,
                "user_id": image.user_id
            }
            fake_db[idx] = updated_image
            return updated_image
    raise HTTPException(status_code=404, detail="Image not found")

@router.delete("/{id}")
async def delete_image(id: int):
    for idx, db_image in enumerate(fake_db):
        if db_image["id"] == id:
            fake_db.pop(idx)
            return {"message": "Image deleted"}
    raise HTTPException(status_code=404, detail="Image not found")