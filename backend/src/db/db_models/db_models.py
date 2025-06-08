import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# -----------------------------
# Modell: KIImage (KI-Image-Metadaten)
# -----------------------------
class KIImage(Base):
    """
    Tabelle 'ki_image_metadata' für die Speicherung von KI-Image-Metadaten.
    """
    __tablename__ = 'ki_image_metadata'

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    image_name = Column(String(255), nullable=False)
    image_tag = Column(String(128), nullable=False)
    image_description = Column(String(500), nullable=True)
    image_reference = Column(String(255), nullable=True)
    image_provider_id = Column(String(36), nullable=False)  # speichert die UUID des Providers als String (Keycloak user_id)
    image_created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # image_provider_id ist der Fremdschlüssel für den Provider.
    # Die UUID kommt direkt aus dem Keycloak-JWT und ist ein String.

    def __repr__(self):
        return f"<KIImage(id={self.image_id}, name='{self.image_name}', tag='{self.image_tag}')>"
# -----------------------------
# Modell: DICOMMetadata (DICOM-Metadaten)
# -----------------------------
#TO DO: dieses Model an py_model Variante anpassen

class DICOMMetadata(Base):
    """
    Tabelle 'dicom_metadata' für DSGVO-konforme DICOM-Metadaten zur Statistik.
    """
    __tablename__ = "dicom_metadata"

    dicom_id = Column(Integer, primary_key=True, index=True)
    dicom_modality = Column(String(10), nullable=True)
    dicom_sop_class_uid = Column(String(64), nullable=True)
    dicom_manufacturer = Column(String(100), nullable=True)
    dicom_rows = Column(Integer, nullable=True)
    dicom_columns = Column(Integer, nullable=True)
    dicom_bits_allocated = Column(Integer, nullable=True)
    dicom_photometric_interpretation = Column(String(20), nullable=True)
    dicom_transfer_syntax_uid = Column(String(64), nullable=True)
    dicom_file_path = Column(String(255), nullable=True)
    dicom_created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))


    def __repr__(self):
        return (f"<DICOMMetadata(id={self.dicom_id}, modality='{self.dicom_modality}', "
                f"sop_class_uid='{self.dicom_sop_class_uid}')>")
