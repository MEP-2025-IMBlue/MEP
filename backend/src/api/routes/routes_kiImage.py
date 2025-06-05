# FastAPI & Dependency Injection
from datetime import timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends

# Datenbank (SQLAlchemy)
from sqlalchemy.orm import Session
from src.db.database.database import get_db
from src.db.crud import crud_kiImage
from src.db.core.exceptions import NoKIImagesInTheList, KIImageNotFound, DatabaseError

# API Models (Pydantic)
from src.api.py_models.py_models import *

# Logger-Funktion
from src.utils.event_logger import log_event

# Services (Image-Logik)
from src.services.image_upload import service_KIImage

# Externe Libraries
import logging
import docker
from typing import List

router = APIRouter(tags=["KI-Image"])
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

# ========================================
# Liste aller KI-Images holen
# ========================================
@router.get("/ki-images", response_model= List[KIImageMetadata], description="""
Returns a list of all currently stored KI-images from the database.
-> If at least one KI-image exists, the response is a JSON array of image objects.
-> If no KI-images are found, an error with status code 404 is returned.
-> If a database error occurs, an error with status code 500 is returned.
""",
    responses={
        200: {"description": "List of stored KI-images"},
        404: {"description": "No KI-images found in the database"},
        500: {"description": "Internal server error due to a database issue"}
    })
async def list_ki_images(db: Session = Depends(get_db)):
    try:
        images = crud_kiImage.get_all_ki_images(db)
        for image in images:
            image.image_created_at = image.image_created_at.astimezone(timezone.utc).isoformat()
        log_event("KI_IMAGE", "list_success", f"{len(images)} Einträge geladen", "INFO")
        return images
    except NoKIImagesInTheList as e:
        log_event("KI_IMAGE", "not_found", "Keine KI-Images gefunden", "WARNING")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        log_event("KI_IMAGE", "db_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
async def list_ki_images(db: Session = Depends(get_db)):
    try:
        images = crud_kiImage.get_all_ki_images(db)
        # Konvertiere image_created_at zu UTC mit ISO-Format
        for image in images:
            image.image_created_at = image.image_created_at.astimezone(timezone.utc).isoformat()
        return images
    except NoKIImagesInTheList as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# Bestimmtes KI-Image per Image-ID holen
# ========================================
@router.get("/ki-images/{image_id}", response_model=KIImageMetadata, description="""
Retrieves a single KI-image by its unique ID.
-> If the KI-image with the specified `image_id` exists, its metadata is returned as a JSON object.  
-> If no KI-image is found with the given ID, a 404 error is returned.  
-> If a database error occurs during the query, a 500 error is returned.
""",
    responses={
        200: {"description": "Metadata of the requested KI-image"},
        404: {"description": "No KI-image found with the given ID"},
        500: {"description": "Internal server error due to a database issue"}
    })
async def get_ki_image(image_id: int, db: Session = Depends(get_db)):
    
    try:
        image = crud_kiImage.get_ki_image_by_id(db, image_id)
        image.image_created_at = image.image_created_at.astimezone(timezone.utc).isoformat()
        log_event("KI_IMAGE", "get_success", f"ID: {image_id} abgerufen", "INFO")
        return image 
    except KIImageNotFound as e:
        log_event("KI_IMAGE", "not_found", f"ID: {image_id} nicht gefunden", "WARNING")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        log_event("KI_IMAGE", "db_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
# ========================================
# KI-Image lokal hochladen
# ========================================
@router.post("/ki-images/local", response_model=KIImageMetadata, description="""
Uploads a Docker image as a `.tar` file and stores its metadata in the database.
-> Requires a `.tar` file upload containing the Docker image.
-> Extracts image name and tag from the loaded image.
-> If successful, stores the image metadata in the database and returns the created KI-Image object.
-> If the file is missing or invalid (e.g., cannot extract image data), a 400 error is returned.
-> If a database error occurs while saving the image metadata, a 500 error is returned.
-> If any other unexpected error occurs during the process, a 500 error is returned.
""",
responses={
    200: {"description": "Local KI-Image successfully uploaded and saved"},
    400: {"description": "Missing or invalid image file"},
    500: {"description": "Internal server error during image processing or database operation"}
}
)
async def upload_local_ki_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_bytes = await file.read()
        log_event("KI_IMAGE", "upload_start", f"Dateiname: {file.filename}", "INFO")
        image_data = service_KIImage.import_local_image(file_bytes=file_bytes)
        log_event("KI_IMAGE", "import_success", f"{image_data['image_reference']} erfolgreich importiert", "INFO")
        db_image = crud_kiImage.create_ki_image(db, image_data)
        log_event("KI_IMAGE", "db_entry_success", f"In Datenbank gespeichert: {db_image.image_reference}", "INFO")
        return db_image
    except ValueError as e:
        log_event("KI_IMAGE", "validation_error", str(e), "WARNING")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        log_event("KI_IMAGE", "db_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log_event("KI_IMAGE", "unexpected_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
# ========================================
# KI-Image von DockerHub hochladen
# ========================================
@router.post(
    "/ki-images/hub", 
    response_model=KIImageMetadata,
    description="""
    Pulls a Docker image from Docker Hub and stores its metadata in the database.
    -> If the image is successfully pulled and metadata stored, the new KI-Image object is returned.
    -> If the image reference is missing or invalid, a 400 error is returned.
    -> If a database error occurs while storing the image, a 500 error is returned.
    -> If any other unexpected error occurs during the process, a 500 error is returned.
    """,
    responses={
        200: {"description": "KI-Image successfully pulled and saved"},
        400: {"description": "Invalid or missing image reference"},
        500: {"description": "Internal server error during image pull or database operation"}
    }
)
async def pull_ki_image(
    image_reference: str = Form(...),
    db: Session = Depends(get_db)
):
    log_event("KI_IMAGE", "pull_start", f"Referenz: {image_reference}", "INFO")
    try:
        image_data = service_KIImage.import_hub_repositorie_image(image_reference=image_reference)
        log_event("KI_IMAGE", "pull_success", f"{image_data['image_reference']} erfolgreich gepullt", "INFO")
        db_image = crud_kiImage.create_ki_image(db, image_data)
        log_event("KI_IMAGE", "db_entry_success", f"In Datenbank gespeichert: {db_image.image_reference}", "INFO")
        return db_image
    except ValueError as e:
        log_event("KI_IMAGE", "validation_error", str(e), "WARNING")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        log_event("KI_IMAGE", "db_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during dockerhub pull")
        log_event("KI_IMAGE", "unexpected_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail="Unerwarteter Fehler beim KI-Image-Pull")

## ========================================
# KI-Image löschen 
# ========================================
@router.delete("/ki-images/{image_id}", description="""
Deletes a specific KI-Image from the database by its ID.
-> If a KI-Image with the given `image_id` exists, it is removed. 
-> If no KI-Image is found with the specified ID, a 404 error is returned.  
-> If a database error occurs during deletion, a 500 error is returned.
""",
    responses={
        200: {"description": "KI-Image successfully deleted"},
        404: {"description": "No KI-Image found with the given ID"},
        500: {"description": "Internal server error due to a database issue"}
    })
async def delete_ki_image_route(image_id: int, db: Session = Depends(get_db)):
    try:
        deleted_image = crud_kiImage.delete_ki_image(db, image_id)
        log_event("KI_IMAGE", "delete_success", f"ID: {image_id} gelöscht", "INFO")
        return {"message": f"KI-Image mit der ID {image_id} wurde gelöscht."}
    except KIImageNotFound as e:
        log_event("KI_IMAGE", "not_found", f"ID: {image_id} nicht gefunden", "WARNING")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        log_event("KI_IMAGE", "db_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# KI-Image ändern
# ========================================
@router.patch("/ki-images/{image_id}", response_model=KIImageMetadata, description="""
Updates the metadata of a KI-Image by its ID. 
-> Only the fields provided in the request will be updated.  
-> If the KI-Image does not exist, a 404 error is returned.  
-> If any provided values are invalid (e.g., empty strings for image_name or image_tag), a 422 error is returned.
""",
    responses={
        200: {"description": "KI-Image metadata successfully updated"},
        404: {"description": "KI-Image with given ID not found"},
        422: {"description": "Validation failed – empty or invalid fields"},
        500: {"description": "Database error during update"}
    })
async def patch_ki_image(image_id: int, updated_ki_image: KIImageUpdate, db: Session = Depends(get_db)):
    try:
        update_data = updated_ki_image.model_dump(exclude_unset=True)
        result = crud_kiImage.update_ki_image(db, image_id, update_data)
        log_event("KI_IMAGE", "update_success", f"ID: {image_id} erfolgreich geändert", "INFO")
        return result
    except KIImageNotFound as e:
        log_event("KI_IMAGE", "not_found", f"ID: {image_id} nicht gefunden", "WARNING")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        log_event("KI_IMAGE", "db_error", str(e), "ERROR")
        raise HTTPException(status_code=500, detail=str(e))