from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_models.db_models import DICOMMetadata
from src.db.core.exceptions import *


def create_dicom(db: Session, dicom_data: dict):
    try:
        db_dicom = DICOMMetadata(**dicom_data)
        db.add(db_dicom)
        db.commit()
        db.refresh(db_dicom)
        return db_dicom
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Erstellen eines DICOM-Datensatzes.") from e

def get_dicom_by_id(db: Session, dicom_id: int):
    try:
        dicom = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_id == dicom_id).first()
        if not dicom:
            raise DICOMNotFound(f"DICOM mit ID {dicom_id} nicht gefunden.")
        return dicom
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Abrufen eines DICOM-Datensatzes.") from e

def get_all_dicoms(db: Session, skip: int = 0, limit: int = 100):
    try:
        dicoms = db.query(DICOMMetadata).offset(skip).limit(limit).all()
        if not dicoms:
            raise NoDICOMInTheList("Keine DICOM-Datensätze in der Datenbank.")
        return dicoms
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Lesen der DICOM-Datenbank.") from e

def update_dicom(db: Session, dicom_id: int, update_data: dict):
    try:
        dicom = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_id == dicom_id).first()
        if not dicom:
            raise DICOMNotFound(f"DICOM mit ID {dicom_id} nicht gefunden.")
        for key, value in update_data.items():
            setattr(dicom, key, value)
        db.commit()
        db.refresh(dicom)
        return dicom
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Aktualisieren eines DICOM-Datensatzes.") from e

def delete_dicom(db: Session, dicom_id: int):
    try:
        dicom = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_id == dicom_id).first()
        if not dicom:
            raise DICOMNotFound(f"DICOM mit ID {dicom_id} nicht gefunden.")
        db.delete(dicom)
        db.commit()
        return dicom
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Löschen eines DICOM-Datensatzes.") from e
