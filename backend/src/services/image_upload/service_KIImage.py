from backend.src.api.py_models import KIImageMetadata
from typing import List

# Simulierte In-Memory-Datenbank
fake_db: List[KIImageMetadata] = []

####Exceptions####
class KIImageNotFoundError(Exception): pass
class NOKIImagesInTheList(Exception): pass


####Funktionen####
def get_all_ki_image():
    if len(fake_db) == 0:
        raise NOKIImagesInTheList()
    else:
        return fake_db

def delete_ki_image(image_id: str):
    for idx, KIImage in enumerate(fake_db):
        if KIImage.image_id == image_id:
            return fake_db.pop(idx)       
    raise KIImageNotFoundError()