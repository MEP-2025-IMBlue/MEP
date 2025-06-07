from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.api.py_models import py_models
from src.db.db_models import db_models
from src.db.core.exceptions import *

#TODO: maybe in crud_kiImage.py
def store_medical_info(db: Session, ki_image_id: int, medical_info: py_models.KIImageInfo):
    """Aktualisiert einen bestehenden KIImage-Eintrag mit medizinischen Zusatzinformationen."""
    try:
        # 1. Bestehenden Datensatz holen
        db_obj = db.query(db_models.KIImage).filter_by(image_id=ki_image_id).first()
        if not db_obj:
            raise KIImageNotFound(f"Kein KIImage mit ID {ki_image_id} gefunden.")

        # 2. Daten aus dem Pydantic-Modell extrahieren
        update_data = medical_info.model_dump()

        # 3. Felder aktualisieren
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        # 4. Änderungen speichern
        db.commit()
        db.refresh(db_obj)

    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Fehler beim Speichern der KI-Image Informationen.") from e

def store_container_config(db: Session, ki_image_id: int, container_config: py_models.ContainerConfigInput):
    """Speichert ein ContainerConfigInput-Objekt(pydantic) als ContainerConfiguration-Eintrag(SQLAlchemy) in der DB."""

    try:
        # Manuelle FK-Prüfung
        if not db.query(db_models.KIImage).filter_by(image_id=ki_image_id).first():
            raise DatabaseError(f"KI-Image mit ID {ki_image_id} wurde nicht gefunden.")

        db_data = container_config.model_dump(exclude_unset=True)
        db_obj = db_models.ContainerConfiguration(ki_image_id=ki_image_id, **db_data)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Fehler beim Speichern der Container Konfiguration.") from e

def get_container_config_by_id(db: Session, ki_image_id: int) -> db_models.ContainerConfiguration:
    """Holt ein ContainerConfiguration-Objekt(SQLAlchemy) anhand der KI-Image-ID."""

    try:
        container_config = db.query(db_models.ContainerConfiguration).filter_by(ki_image_id=ki_image_id).first()
        if not container_config:
            raise KIImageNotFound(f"Konfiguration für das Image mit ID {ki_image_id} nicht gefunden.")
        return container_config
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Abrufen der Container-Konfiguration.") from e

def patch_container_config_by_id(db: Session, ki_image_id: int):
    """Ändert ein ContainerConfiguration-Objekt(SQLAlchemy) anhand der KI-Image-ID."""
    pass

def delete_container_config_by_id(db: Session, ki_image_id: int):
    """Löscht ein ContainerConfiguration-Objekt(SQLAlchemy) anhand der KI-Image-ID."""

    try:
        container_config = db.query(db_models.ContainerConfiguration).filter_by(ki_image_id = ki_image_id).first()
        if not container_config:
            raise KIImageNotFound(f"Konfiguration für das Image mit ID {ki_image_id} nicht gefunden.")

        db.delete(container_config)
        db.commit()
        return container_config
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Fehler beim Löschen der Container Konfiguration.") from e

    