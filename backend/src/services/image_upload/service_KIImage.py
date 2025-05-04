from backend.src.api.py_models import KIImageMetadata
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

def get_ki_image_by_id(image_id: str):
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
