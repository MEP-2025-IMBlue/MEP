from backend.src.api.py_models import KIImageMetadata
from typing import List

# Simulierte In-Memory-Datenbank
fake_db: List[KIImageMetadata] = []

####Exceptions####
class KIImageNotFoundError(Exception): pass
class NOKIImagesInTheList(Exception): pass
class InvalidImageIndexError(Exception): pass


####Funktionen####
def get_all_ki_image():
    if len(fake_db) == 0:
        raise NOKIImagesInTheList()
    else:
        return fake_db
    
def get_ki_image_by_id(image_id: str):
    if not image_id:
        raise InvalidImageIndexError()
    for ki_image in fake_db:
        if ki_image.image_id == image_id:
            return ki_image
    raise KIImageNotFoundError()

def add_ki_image(KIimage: KIImageMetadata):
    for entry in fake_db:
        if entry.image_id == KIimage.image_id:
            raise ValueError(f"Ein Bild mit der ID {KIimage.image_id} existiert bereits.")
    
    fake_db.append(KIimage)
    return KIimage

def delete_ki_image(image_id: str):
    for idx, KIimage in enumerate(fake_db):
        if KIimage.image_id == image_id:
            return fake_db.pop(idx)       
    raise KIImageNotFoundError()