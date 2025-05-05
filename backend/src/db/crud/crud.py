"""
crud.py
-------------
Enthält die CRUD-Operationen (Create, Read, Update, Delete) für KI-Image-Metadaten.
Pfad: backend/src/crud/crud.py
"""
from sqlalchemy.orm import Session
from src.db.db_models import db_models  # Importiere die Modelle

def create_ki_image(db: Session, image_data: dict):
    """
    Erstellt einen neuen Eintrag in der Tabelle ki_image_metadata.
    """
    db_ki_image = db_models.KIImage(**image_data)
    db.add(db_ki_image)
    db.commit()
    db.refresh(db_ki_image)
    return db_ki_image

def get_ki_image_by_id(db: Session, image_id: int):
    """
    Gibt ein Bild-Objekt anhand seiner ID zurück oder None, falls nicht gefunden.
    """
    return db.query(db_models.KIImage).filter(db_models.KIImage.image_id == image_id).first()

def get_all_ki_images(db: Session, skip: int = 0, limit: int = 100):
    """
    Gibt eine Liste aller Bilder zurück (mit optionalem Paging).
    """
    return db.query(db_models.KIImage).offset(skip).limit(limit).all()

def update_ki_image(db: Session, image_id: int, update_data: dict):
    """
    Aktualisiert ein Bild anhand seiner ID und Rückgabe des aktualisierten Objekts.
    """
    db_ki_image = db.query(db_models.KIImage).filter(db_models.KIImage.image_id == image_id).first()
    if db_ki_image:
        for key, value in update_data.items():
            setattr(db_ki_image, key, value)
        db.commit()
        db.refresh(db_ki_image)
    return db_ki_image

def delete_ki_image(db: Session, image_id: int):
    """
    Löscht ein Bild anhand seiner ID.
    """
    db_ki_image = db.query(db_models.KIImage).filter(db_models.KIImage.image_id == image_id).first()
    if db_ki_image:
        db.delete(db_ki_image)
        db.commit()
    return db_ki_image
