"""
crud_dicom.py
-----------------
Enthält CRUD-Operationen für die DICOM-Metadaten.
Pfad: backend/src/db/crud/crud_dicom.py
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_models.db_models import DICOMMetadata
from src.db.core.exceptions import DICOMNotFound, DatabaseError


def create_dicom(db: Session, metadata: dict) -> DICOMMetadata:
    """
    Erstellt einen neuen DICOM-Metadatensatz in der Datenbank.

    - Gibt das erstellte DICOMMetadata-Objekt zurück.
    - Loggt den Vorgang.
    - Wirft Exception bei Fehlern (nicht typisiert).
    """
    try:
        dicom_entry = DICOMMetadata(**metadata)
        db.add(dicom_entry)
        db.commit()
        db.refresh(dicom_entry)
        logging.info(f"[DB] Neuer DICOM-Eintrag erstellt: {dicom_entry}")
        return dicom_entry
    except Exception as e:
        logging.error(f"[DB] Fehler beim Erstellen des DICOM-Eintrags: {e}")
        raise


def get_dicom_metadata_by_uuid(db: Session, uuid: str) -> DICOMMetadata:
    """
    Ruft einen DICOM-Metadatensatz anhand der UUID ab.

    - Gibt das DICOMMetadata-Objekt zurück.
    - Wirft DICOMNotFound, wenn kein Eintrag existiert.
    - Wirft DatabaseError bei SQLAlchemy-Fehlern.
    """
    try:
        entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_uuid == uuid).first()
        if not entry:
            logging.warning(f"[DB] DICOM mit UUID {uuid} nicht gefunden.")
            raise DICOMNotFound(f"DICOM-Metadaten mit UUID {uuid} nicht gefunden.")
        logging.info(f"[DB] DICOM-Metadaten mit UUID {uuid} abgerufen.")
        return entry
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Abrufen eines DICOM-Eintrags: {e}")
        raise DatabaseError("Fehler beim Abrufen eines DICOM-Metadatensatzes.") from e


def update_dicom_metadata(db: Session, uuid: str, updates: dict) -> DICOMMetadata:
    """
    Aktualisiert bestimmte Felder eines vorhandenen DICOM-Metadatensatzes.

    - Gibt das aktualisierte Objekt zurück.
    - Wirft DICOMNotFound, wenn kein Eintrag mit der UUID existiert.
    - Wirft DatabaseError bei SQLAlchemy-Fehlern.
    """
    try:
        entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_uuid == uuid).first()
        if not entry:
            logging.warning(f"[DB] Update fehlgeschlagen – DICOM UUID {uuid} nicht gefunden.")
            raise DICOMNotFound(f"DICOM-Metadaten mit UUID {uuid} nicht gefunden.")

        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        db.commit()
        db.refresh(entry)
        logging.info(f"[DB] DICOM UUID {uuid} erfolgreich aktualisiert.")
        return entry
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Aktualisieren eines DICOM-Eintrags: {e}")
        raise DatabaseError("Fehler beim Aktualisieren eines DICOM-Eintrags.") from e


def delete_dicom_metadata(db: Session, uuid: str) -> bool:
    """
    Löscht einen DICOM-Metadatensatz anhand der UUID.

    - Gibt True bei erfolgreichem Löschen zurück.
    - Wirft DICOMNotFound, wenn kein Eintrag existiert.
    - Wirft DatabaseError bei SQLAlchemy-Fehlern.
    """
    try:
        entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_uuid == uuid).first()
        if not entry:
            logging.warning(f"[DB] Löschvorgang – DICOM UUID {uuid} nicht gefunden.")
            raise DICOMNotFound(f"DICOM-Metadaten mit UUID {uuid} nicht gefunden.")

        db.delete(entry)
        db.commit()
        logging.info(f"[DB] DICOM UUID {uuid} erfolgreich gelöscht.")
        return True
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Löschen eines DICOM-Eintrags: {e}")
        raise DatabaseError("Fehler beim Löschen eines DICOM-Eintrags.") from e


def create_or_replace_dicom_metadata(db: Session, metadata: dict) -> DICOMMetadata:
    """
    Erstellt einen neuen DICOM-Metadatensatz oder ersetzt einen vorhandenen mit derselben UUID.

    - Gibt das neu angelegte Objekt zurück.
    - Falls vorhanden, wird der alte Datensatz gelöscht.
    - Rollback bei Fehlern.
    - Wirft DatabaseError bei allen Ausnahmen.
    """
    try:
        existing = db.query(DICOMMetadata).filter_by(dicom_uuid=metadata["dicom_uuid"]).first()

        if existing:
            db.delete(existing)
            db.commit()
            logging.info(f"[DB] Bestehender DICOM-Eintrag mit UUID {metadata['dicom_uuid']} wurde ersetzt.")

        new_entry = DICOMMetadata(**metadata)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        logging.info(f"[DB] Neuer DICOM-Eintrag gespeichert: {new_entry}")

        return new_entry

    except Exception as e:
        db.rollback()
        logging.error(f"[DB] Fehler bei create_or_replace für UUID {metadata.get('dicom_uuid')}: {e}")
        raise DatabaseError(f"[DB] Fehler beim Erstellen oder Ersetzen des DICOM-Eintrags: {str(e)}")
