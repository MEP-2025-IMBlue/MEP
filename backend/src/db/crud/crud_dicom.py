from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_models.db_models import DICOMMetadata
from src.db.core.exceptions import DICOMNotFound, DatabaseError
import logging


# Erstellt einen neuen DICOM-Metadatensatz in der Datenbank -> GET
def create_dicom(db: Session, metadata: dict) -> DICOMMetadata:
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


# # Ruft einen DICOM-Metadatensatz anhand der UUID ab
# def get_dicom_metadata_by_uuid(db: Session, uuid: str) -> DICOMMetadata:
#     try:
#         entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_uuid == uuid).first()
#         if not entry:
#             raise DICOMNotFound(f"DICOM-Metadaten mit UUID {uuid} nicht gefunden.")
#         return entry
#     except SQLAlchemyError as e:
#         raise DatabaseError("Fehler beim Abrufen eines DICOM-Metadatensatzes.") from e


# # Aktualisiert bestimmte Felder eines vorhandenen DICOM-Metadatensatzes
# def update_dicom_metadata(db: Session, uuid: str, updates: dict) -> DICOMMetadata:
#     try:
#         entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_uuid == uuid).first()
#         if not entry:
#             raise DICOMNotFound(f"DICOM-Metadaten mit UUID {uuid} nicht gefunden.")

#         for key, value in updates.items():
#             if hasattr(entry, key):
#                 setattr(entry, key, value)

#         db.commit()
#         db.refresh(entry)
#         return entry
#     except SQLAlchemyError as e:
#         raise DatabaseError("Fehler beim Aktualisieren eines DICOM-Eintrags.") from e


# Löscht einen DICOM-Metadatensatz anhand der UUID
def delete_dicom_metadata(db: Session, uuid: str) -> bool:
    try:
        entry = db.query(DICOMMetadata).filter(DICOMMetadata.dicom_uuid == uuid).first()
        if not entry:
            raise DICOMNotFound(f"DICOM-Metadaten mit UUID {uuid} nicht gefunden.")

        db.delete(entry)
        db.commit()
        return True
    except SQLAlchemyError as e:
        raise DatabaseError("Fehler beim Löschen eines DICOM-Eintrags.") from e


# # Erstellt einen neuen DICOM-Metadatensatz oder ersetzt einen vorhandenen mit derselben UUID
# def create_or_replace_dicom_metadata(db: Session, metadata: dict) -> DICOMMetadata:
#     try:
#         existing = db.query(DICOMMetadata).filter_by(
#             dicom_uuid=metadata["dicom_uuid"]
#         ).first()

#         if existing:
#             db.delete(existing)
#             db.commit()

#         new_entry = DICOMMetadata(**metadata)
#         db.add(new_entry)
#         db.commit()
#         db.refresh(new_entry)

#         return new_entry

#     except Exception as e:
#         db.rollback()
#         raise DatabaseError(f"[DB] Fehler beim Erstellen oder Ersetzen des DICOM-Eintrags: {str(e)}")

 