from fastapi import APIRouter, HTTPException
from backend.src.api.py_models import KIImageMetadata
from backend.src.services.image_upload.service_KIImage import *

#An M: was ist prefix?
#router = APIRouter(prefix="/images", tags=["images"])
router = APIRouter()

@router.get("/list-KIimages", description= """
Gibt eine Liste aller derzeit gespeicherten KI-Bilder aus der Datenbank zurück.
-> Wenn mindestens ein Eintrag vorhanden ist, enthält die Antwort eine Liste unter dem Schlüssel `"KI-Images"`.
-> Wenn keine Bilder vorhanden sind, wird ein Fehler mit Statuscode 404 zurückgegeben.
""",
    responses={
        200: {"description": "Liste der gespeicherten KI-Bilder"},
        404: {"description": "Es befinden sich keine KI-Bilder in der Datenbank"}
    })
async def list_KIimages():
    try:
        list = get_all_ki_image()
        return {"KI-Images" : list}
    except NOKIImagesInTheList:
        raise HTTPException(status_code=404, detail=f"Es befinden sich noch keine KI-Images in der Datenbank.")

@router.get("/get-KIimage/{image_id}", response_model=KIImageMetadata, description="""
Gibt ein einzelnes KI-Bild mit der angegebenen `image_id` zurück.
-> Wenn ein entsprechendes KI-Bild gefunden wird, wird es als Objekt zurückgegeben.
-> Wenn kein Eintrag zur angegebenen ID existiert, wird ein Fehler mit Statuscode 404 zurückgegeben.
-> Bei ungültigem ID-Format wird ein Fehler mit Statuscode 400 zurückgegeben.
""",
    responses={
        200: {"description": "KI-Bild erfolgreich gefunden"},
        400: {"description": "Ungültiges Image-ID-Format"},
        404: {"description": "Kein KI-Bild mit der angegebenen ID gefunden"}
    }
)
async def get_KIimage(image_id: str):
    try:
        return get_ki_image_by_id(image_id)
    except InvalidImageIndexError:
        raise HTTPException(status_code=400, detail="Ungültiges Image-ID-Format")
    except KIImageNotFoundError:
        raise HTTPException(status_code=404, detail=f"KI-Image mit der ID {image_id} wurde nicht gefunden.")

@router.post("/add-KIimage", response_model = KIImageMetadata, description = """
Erstellt einen neuen Datensatz für ein KI-Image des Providers mit den angegebenen Metadaten.
Die Metadaten werden in der Datenbank gespeichert (hier simuliert mit `fake_db`).
""",
    responses={
        200: {"description": "KI-Image erfolgreich erstellt"},
        400: {"description": "Ein KI-Image mit dieser ID existiert bereits"},
        422: {"description": "Ungültige Anfrage – erforderliche Felder fehlen oder sind falsch"}
    })
async def add_KIimage(KIimage: KIImageMetadata):
    try:
        return add_ki_image(KIimage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete-KIimage/{image_id}", description= """
Löscht ein KI-Bild mit der angegebenen `image_id` aus der Datenbank:
Durchsucht die Datenbank nach einem Eintrag mit passender ID.
-> Gibt eine Bestätigung zurück, wenn das Bild erfolgreich gelöscht wurde.
-> Wenn kein entsprechender Eintrag gefunden wird, wird ein Fehler mit dem Statuscode 404 zurückgegeben.
""", responses={
        200: {"description": "Bild erfolgreich gelöscht"},
        404: {"description": "Kein KI-Bild mit der angegebenen ID gefunden"}
    })
async def delete_KIimage(image_id: str):
    try:
        deleted = delete_ki_image(image_id)
        return {"message": f"KI-Image mit der ID {deleted.image_id} wurde gelöscht."}
    except KIImageNotFoundError:
        raise HTTPException(status_code=404, detail=f"KI-Image mit der ID {image_id} wurde nicht gefunden.")

# @router.put("/{id}", response_model=KIImageMetadata)


