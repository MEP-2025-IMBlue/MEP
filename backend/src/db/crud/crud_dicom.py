from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_models.db_models import DICOMMetadata
from src.db.core.exceptions import DICOMNotFound, DatabaseError
from typing import List
import logging

# Speichert das DICOM-Metadaten in der Datenbank
def store_dicom_metadata(db: Session, metadata: dict):
    """
    Erstellt einen neuen DICOM-Metadatensatz in der Datenbank.
    
    Args:
        db (Session): SQLAlchemy-Datenbanksitzung.
        metadata (dict): DSGVO-konforme Metadaten (dicom_modality, dicom_sop_class_uid, etc.).
    
    Returns:
        DICOMMetadata: Ersteller Datenbankeintrag.
    
    Raises:
        DatabaseError: Bei Fehlern während der Datenbankoperation.
    """
    try:
        dicom_entry = DICOMMetadata(**metadata)
        db.add(dicom_entry)
        db.commit()
        db.refresh(dicom_entry)
        logging.info(f"[DB] Neuer DICOM-Eintrag erstellt: {dicom_entry}")
        #return dicom_entry
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[DB] Fehler beim Erstellen des DICOM-Eintrags: {e}")
        raise DatabaseError(f"Fehler beim Erstellen des DICOM-Eintrags: {str(e)}")

# Listet alle DICOM-Metadatens aus der Datenbank
def list_dicom_metadata(db: Session) -> List[DICOMMetadata]:
    """
    Listet alle DICOM-Metadatensätze aus der Datenbank.
    
    Args:
        db (Session): SQLAlchemy-Datenbanksitzung.
    
    Returns:
        List[DICOMMetadata]: Liste aller DICOM-Metadatensätze.
    
    Raises:
        DatabaseError: Bei Fehlern während der Datenbankoperation.
    """
    try:
        entries = db.query(DICOMMetadata).all()
        logging.info(f"[DB] {len(entries)} DICOM-Metadatensätze abgerufen.")
        return entries
    except SQLAlchemyError as e:
        logging.error(f"[DB] Fehler beim Abrufen der DICOM-Metadaten: {e}")
        raise DatabaseError(f"Fehler beim Abrufen der DICOM-Metadaten: {str(e)}")

# Löscht einen DICOM-Metadatensatz aus der Datenbank
def delete_dicom_metadata(db: Session, dicom_id: int) -> bool:
    """
    Löscht einen DICOM-Metadatensatz anhand der dicom_id.
    
    Args:
        db (Session): SQLAlchemy-Datenbanksitzung.
        dicom_id (int): ID des zu löschenden DICOM-Eintrags.
    
    Returns:
        bool: True, wenn Löschung erfolgreich.
    
    Raises:
        DICOMNotFound: Wenn kein Eintrag mit der dicom_id gefunden wird.
        DatabaseError: Bei Fehlern während der Datenbankoperation.
    """
    try:
        entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_id == dicom_id).first()
        if not entry:
            logging.error(f"[DB] DICOM-Eintrag mit ID {dicom_id} nicht gefunden.")
            raise DICOMNotFound(f"DICOM-Metadaten mit ID {dicom_id} nicht gefunden.")
        
        db.delete(entry)
        db.commit()
        logging.info(f"[DB] DICOM-Eintrag mit ID {dicom_id} gelöscht.")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"[DB] Fehler beim Löschen des DICOM-Eintrags: {e}")
        raise DatabaseError(f"Fehler beim Löschen des DICOM-Eintrags: {str(e)}")