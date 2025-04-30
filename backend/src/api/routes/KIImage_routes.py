from fastapi import APIRouter, HTTPException
from backend.src.api.py_models import KIImageMetadata
from typing import List

#An M: was ist prefix?
#router = APIRouter(prefix="/images", tags=["images"])
router = APIRouter()

# Simulierte In-Memory-Datenbank
fake_db = []

@router.get("/list-KIimages", description= """
Gibt eine Liste aller derzeit gespeicherten KI-Bilder aus der Datenbank zurück.
- Wenn keine Bilder vorhanden sind, wird eine entsprechende Nachricht zurückgegeben.
- Die Antwort enthält entweder eine Liste unter dem Schlüssel `"KI-Images"` oder eine `"message"`, dass noch keine Einträge vorhanden sind.
""")
async def list_KIimages():
    if len(fake_db) == 0:
        return {"message":"No KIImages yet!"}
    return {"KI-Images": fake_db}

@router.get("/get-KIimage/{image_id}", response_model=KIImageMetadata)
async def get_KIimage(image_id: int):
    if image_id < 0 or image_id >= len(fake_db):
        pass
    # for image in fake_db:
    #     if image["id"] == id:
    #         return image
    #raise HTTPException(status_code=404, detail="Image not found")

@router.post("/add-KIimage", response_model = KIImageMetadata, description = """
Erstellt einen neuen Datensatz für ein KI-Image des Providers mit den angegebenen Metadaten.

- Die Metadaten werden in der Datenbank gespeichert (hier simuliert mit `fake_db`).
- Die Anfrage muss alle erforderlichen Felder des `KIImageMetadata`-Modells enthalten.
- Gibt die gespeicherten Metadaten als Bestätigung zurück.
""")
async def add_KIimage(KIimage: KIImageMetadata):
    fake_db.append(KIimage)
    return KIimage

@router.delete("/delete-KIimage/{image_id}", description= """
Löscht ein KI-Bild mit der angegebenen `image_id` aus der Datenbank.

- Durchsucht die Datenbank nach einem Eintrag mit passender ID.
- Gibt eine Bestätigung zurück, wenn das Bild erfolgreich gelöscht wurde.
- Wenn kein entsprechender Eintrag gefunden wird, wird ein Fehler mit dem Statuscode 404 zurückgegeben.
""", responses={
        200: {"description": "Bild erfolgreich gelöscht"},
        404: {"description": "Kein KI-Bild mit der angegebenen ID gefunden"}
    })
async def delete_KIimage(image_id: str):
    for idx, KIImageMetadata in enumerate(fake_db):
        if KIImageMetadata.image_id == image_id:
            fake_db.pop(idx)
            return {"message": f"Image with the id {image_id} deleted"}
    raise HTTPException(status_code=404, detail=f"KI-Image with {image_id} not found")

# @router.put("/{id}", response_model=KIImageMetadata)
# async def update_image(id: int, image: KIImageMetadata):
#     for idx, db_image in enumerate(fake_db):
#         if db_image["id"] == id:
#             updated_image = {
#                 "id": id,
#                 "name": image.name,
#                 "image_tag": image.image_tag,
#                 "description": image.description,
#                 "image_path": image.image_path,
#                 "user_id": image.user_id
#             }
#             fake_db[idx] = updated_image
#             return updated_image
#     raise HTTPException(status_code=404, detail="Image not found")

