from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from src.api.py_models import *
#from src.services.image_upload.service_KIImage import *
from src.db.database.database import get_db
from src.db.crud import crud
import logging
import json
import tempfile
import docker
import os

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
docker_client = docker.from_env()

# ------------------------------------------------------------
# Abschnitt: GET

@router.get("/ki-images", description= """
Gibt eine Liste aller derzeit gespeicherten KI-Bilder aus der Datenbank zurück.
-> Wenn mindestens ein Eintrag vorhanden ist, enthält die Antwort eine Liste unter dem Schlüssel `"KI-Images"`.
-> Wenn keine Bilder vorhanden sind, wird ein Fehler mit Statuscode 404 zurückgegeben.
""",
    responses={
        200: {"description": "Liste der gespeicherten KI-Bilder"},
        404: {"description": "Es befinden sich keine KI-Bilder in der Datenbank"}
    })
async def list_ki_images(db: Session = Depends(get_db)):
    ki_images = crud.get_all_ki_images(db)
    if not ki_images:
        raise HTTPException(status_code=404, detail="Es befinden sich noch keine KI-Images in der Datenbank.")
    return ki_images


@router.get("/ki-images/{image_id}", response_model=KIImageMetadata, description="""
Gibt ein einzelnes KI-Bild mit der angegebenen `image_id` zurück.
-> Wenn ein entsprechendes KI-Bild gefunden wird, wird es als Objekt zurückgegeben.
-> Wenn kein Eintrag zur angegebenen ID existiert, wird ein Fehler mit Statuscode 404 zurückgegeben.
-> Bei ungültigem ID-Format wird ein Fehler mit Statuscode 400 zurückgegeben.
""",
    responses={
        200: {"description": "KI-Bild erfolgreich gefunden"},
        400: {"description": "Ungültiges Image-ID-Format"},
        404: {"description": "Kein KI-Bild mit der angegebenen ID gefunden"}
    })
async def get_ki_image(image_id: int, db: Session = Depends(get_db)):
    ki_image = crud.get_ki_image_by_id(db, image_id)
    if not ki_image:
        raise HTTPException(status_code=404, detail=f"KI-Image mit der ID {image_id} wurde nicht gefunden.")
    return ki_image


# ------------------------------------------------------------
# Abschnitt: POST

@router.post("/upload-local", response_model=KIImageMetadata)  # Upload Image local
async def upload_local_image(image_data: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".tar"):
        logger.error(f"Invalid file extension: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .tar files are allowed")

    try:
        logger.info(f"Processing upload for file: {file.filename}")
        if not image_data or image_data.strip() == "":
            logger.error("image_data is empty or whitespace")
            raise HTTPException(status_code=422, detail="image_data cannot be empty")

        try:
            image_data_dict = json.loads(image_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in image_data: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Invalid JSON in image_data: {str(e)}")

        image_data_model = ImageUpload(**image_data_dict)
        logger.info(f"Validated image_data: {image_data_model.dict()}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as temp_file:
            content = await file.read()
            logger.info(f"Read {len(content)} bytes from uploaded file")
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Temporary file created at: {temp_file_path}")

        local_image_name = f"{image_data_model.name}:{image_data_model.image_tag}"
        logger.info(f"Importing image as: {local_image_name}")
        with open(temp_file_path, "rb") as f:
            images = docker_client.images.load(f.read())
            imported_image = images[0]
            imported_image.tag(local_image_name)
            logger.info(f"Tagged image as: {local_image_name}")

        image_data_dict_db = {
            "image_name": image_data_model.name,
            "image_tag": image_data_model.image_tag,
            "description": image_data_model.description,
            "image_path": None,
            "local_image_name": local_image_name,
            "provider_id": image_data_model.user_id
        }
        created_image = crud.create_ki_image(db, image_data_dict_db)
        logger.info(f"Image metadata saved in DB: {created_image}")

        os.unlink(temp_file_path)
        logger.info(f"Temporary file deleted: {temp_file_path}")
        return created_image

    except docker.errors.APIError as e:
        logger.error(f"Docker API error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to import image: {str(e)}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/ki-images", response_model=KIImageMetadata, description="""
Erstellt einen neuen Datensatz für ein KI-Image des Providers mit den angegebenen Metadaten.
Die Metadaten werden in der Datenbank gespeichert.
""",
    responses={
        200: {"description": "KI-Image erfolgreich erstellt"},
        400: {"description": "Ein KI-Image mit dieser ID existiert bereits"},
        422: {"description": "Ungültige Anfrage – erforderliche Felder fehlen oder sind falsch"}
    })
async def add_ki_image_route(ki_image: KIImageMetadata, db: Session = Depends(get_db)):
    image_data_dict = ki_image.dict(exclude_unset=True)
    created_image = crud.create_ki_image(db, image_data_dict)
    return created_image


# ------------------------------------------------------------
# Abschnitt: DELETE

@router.delete("/ki-images/{image_id}", description="""
Löscht ein KI-Bild mit der angegebenen `image_id` aus der Datenbank:
Durchsucht die Datenbank nach einem Eintrag mit passender ID.
-> Gibt eine Bestätigung zurück, wenn das Bild erfolgreich gelöscht wurde.
-> Wenn kein entsprechender Eintrag gefunden wird, wird ein Fehler mit dem Statuscode 404 zurückgegeben.
""", responses={
        200: {"description": "Bild erfolgreich gelöscht"},
        404: {"description": "Kein KI-Bild mit der angegebenen ID gefunden"}
    })
async def delete_ki_image_route(image_id: int, db: Session = Depends(get_db)):
    deleted_image = crud.delete_ki_image(db, image_id)
    if not deleted_image:
        raise HTTPException(status_code=404, detail=f"KI-Image mit der ID {image_id} wurde nicht gefunden.")
    return {"message": f"KI-Image mit der ID {image_id} wurde gelöscht."}


# ------------------------------------------------------------
# Abschnitt: PATCH

@router.patch("/ki-images/{image_id}", response_model=KIImageMetadata, description="""
Aktualisiert ein KI-Bild mit der angegebenen `image_id`:
Durchsucht die Datenbank nach einem Bild mit der angegebenen ID und aktualisiert die Felder, die im übergebenen JSON enthalten sind.
-> Gibt das aktualisierte Bild zurück, wenn die Änderung erfolgreich war.
-> Wenn kein entsprechendes Bild mit der ID gefunden wird, wird ein Fehler mit dem Statuscode 404 zurückgegeben.
-> Wenn das `image_id`-Format ungültig ist, wird ein Fehler mit dem Statuscode 400 zurückgegeben.
""", responses={
        200: {"description": "Bild erfolgreich aktualisiert"},
        400: {"description": "Ungültiges Image-ID-Format"},
        404: {"description": "Kein KI-Bild mit der angegebenen ID gefunden"}
    })
async def patch_ki_image(image_id: int, updated_ki_image: KIImageUpdate, db: Session = Depends(get_db)):
    update_data = updated_ki_image.model_dump(exclude_unset=True)
    updated = crud.update_ki_image(db, image_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"KI-Image mit der ID {image_id} wurde nicht gefunden.")
    return updated
