"""
crud_kiImage.py
-----------------
Enthält CRUD-Operationen für die KI-Image-Metadaten.
Pfad: backend/src/db/crud/crud_kiImage.py
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_models.db_models import KIImage
from src.db.core.exceptions import NoKIImagesInTheList, DatabaseError, KIImageNotFound


def create_ki_image(db: Session, image_data: dict) -> KIImage:
    """
    Erstellt einen neuen KIImage-Eintrag in der Datenbank.

    - Gibt das erstellte KIImage-Objekt zurück.
    - Wirft DatabaseError bei Datenbankfehlern.
    """
    try:
        db_ki_image = KIImage(**image_data)
        db.add(db_ki_image)
        db.commit()
        db.refresh(db_ki_image)
        logging.info(f"[DB] KI-Image erstellt: {db_ki_image}")
        return db_ki_image
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Erstellen eines KI-Images: {e}")
        raise DatabaseError("Fehler beim Erstellen eines KI-Images.") from e


def get_ki_image_by_id(db: Session, image_id: int) -> KIImage:
    """
    Gibt ein KI-Image anhand seiner ID zurück.

    - Gibt das KIImage-Objekt zurück.
    - Wirft KIImageNotFound, wenn nicht gefunden.
    - Wirft DatabaseError bei SQLAlchemy-Problemen.
    """
    try:
        image = db.query(KIImage).filter(KIImage.image_id == image_id).first()
        if not image:
            logging.warning(f"[DB] KI-Image mit ID {image_id} nicht gefunden.")
            raise KIImageNotFound(f"KI-Image mit ID {image_id} nicht gefunden.")
        logging.info(f"[DB] KI-Image mit ID {image_id} gefunden.")
        return image
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Abrufen eines KI-Images: {e}")
        raise DatabaseError("Fehler beim Abrufen eines KI-Images.") from e


def get_all_ki_images(db: Session, skip: int = 0, limit: int = 100) -> list[KIImage]:
    """
    Gibt eine Liste aller KI-Bilder zurück (paginierbar).

    - Gibt eine Liste von KIImage-Objekten zurück.
    - Wirft NoKIImagesInTheList, wenn keine Einträge existieren.
    - Wirft DatabaseError bei unerwarteten DB-Problemen.
    """
    try:
        images = db.query(KIImage).offset(skip).limit(limit).all()
        if not images:
            logging.warning("[DB] Keine KI-Images in der Datenbank gefunden.")
            raise NoKIImagesInTheList("Es befinden sich keine KI-Bilder in der Datenbank.")
        logging.info(f"[DB] {len(images)} KI-Images abgerufen.")
        return images
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Lesen der Datenbank: {e}")
        raise DatabaseError("Fehler beim Lesen der Datenbank.") from e


def update_ki_image(db: Session, image_id: int, update_data: dict) -> KIImage:
    """
    Aktualisiert ein KI-Bild anhand der ID.

    - Gibt das aktualisierte Objekt zurück.
    - Wirft KIImageNotFound, wenn das Bild nicht existiert.
    - Wirft DatabaseError bei SQLAlchemy-Fehlern.
    """
    try:
        image = db.query(KIImage).filter(KIImage.image_id == image_id).first()
        if not image:
            logging.warning(f"[DB] Update fehlgeschlagen – KI-Image mit ID {image_id} nicht gefunden.")
            raise KIImageNotFound(f"KI-Image mit ID {image_id} nicht gefunden.")

        for key, value in update_data.items():
            setattr(image, key, value)

        db.commit()
        db.refresh(image)
        logging.info(f"[DB] KI-Image mit ID {image_id} aktualisiert.")
        return image
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Aktualisieren eines KI-Images: {e}")
        raise DatabaseError("Fehler beim Aktualisieren eines KI-Images.") from e


def delete_ki_image(db: Session, image_id: int) -> KIImage:
    """
    Löscht ein KI-Image anhand seiner ID.

    - Gibt das gelöschte Objekt zurück.
    - Wirft KIImageNotFound, wenn nicht vorhanden.
    - Wirft DatabaseError bei SQLAlchemy-Fehlern.
    """
    try:
        image = db.query(KIImage).filter(KIImage.image_id == image_id).first()
        if not image:
            logging.warning(f"[DB] Löschvorgang – KI-Image mit ID {image_id} nicht gefunden.")
            raise KIImageNotFound(f"KI-Image mit ID {image_id} nicht gefunden.")

        db.delete(image)
        db.commit()
        logging.info(f"[DB] KI-Image mit ID {image_id} gelöscht.")
        return image
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Löschen eines KI-Images: {e}")
        raise DatabaseError("Fehler beim Löschen eines KI-Images.") from e
