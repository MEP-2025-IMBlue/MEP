"""
crud_kiImage.py
-----------------
Enthält CRUD-Operationen für die KI-Image-Metadaten.
Pfad: backend/src/db/crud/crud_kiImage.py
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_models.db_models import KIImage
from src.db.core.exceptions import NoKIImagesInTheList, DatabaseError, KIImageNotFound


def create_ki_image(db: Session, image_data: dict):
    """
    Erstellt einen neuen KIImage-Eintrag in der Datenbank.
    """
    try:
        db_ki_image = KIImage(**image_data)
        db.add(db_ki_image)
        db.commit()
        db.refresh(db_ki_image)
        return db_ki_image
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Erstellen eines KI-Images.") from e


def get_ki_image_by_id(db: Session, image_id: int):
    """
    Gibt ein KI-Image anhand seiner ID zurück.
    - Wirft KIImageNotFound, wenn nicht gefunden.
    - Wirft DatabaseError bei SQLAlchemy-Problemen.
    """
    try:
        image = db.query(KIImage).filter(KIImage.image_id == image_id).first()
        if not image:
            raise KIImageNotFound(f"KI-Image mit ID {image_id} nicht gefunden.")
        return image
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Abrufen eines KI-Images.") from e


def get_all_ki_images(db: Session, skip: int = 0, limit: int = 100):
    """
    Gibt eine Liste aller KI-Bilder zurück.
    - Wirft NoKIImagesInTheList, wenn keine Einträge existieren.
    - Wirft DatabaseError bei unerwarteten DB-Problemen.
    """
    try:
        images = db.query(KIImage).offset(skip).limit(limit).all()
        if not images:
            raise NoKIImagesInTheList("Es befinden sich keine KI-Bilder in der Datenbank.")
        return images
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Lesen der Datenbank.") from e


def update_ki_image(db: Session, image_id: int, update_data: dict):
    """
    Aktualisiert ein KI-Bild anhand der ID.
    - Wirft KIImageNotFound, wenn das Bild nicht existiert.
    """
    try:
        image = db.query(KIImage).filter(KIImage.image_id == image_id).first()
        if not image:
            raise KIImageNotFound(f"KI-Image mit ID {image_id} nicht gefunden.")

        for key, value in update_data.items():
            setattr(image, key, value)

        db.commit()
        db.refresh(image)
        return image
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Aktualisieren eines KI-Images.") from e


def delete_ki_image(db: Session, image_id: int):
    """
    Löscht ein KI-Image anhand seiner ID.
    - Gibt das gelöschte Objekt zurück.
    - Wirft KIImageNotFound, wenn nicht vorhanden.
    """
    try:
        image = db.query(KIImage).filter(KIImage.image_id == image_id).first()
        if not image:
            raise KIImageNotFound(f"KI-Image mit ID {image_id} nicht gefunden.")

        db.delete(image)
        db.commit()
        return image
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Löschen eines KI-Images.") from e
