# db_models.py
# -------------------------
from sqlalchemy import Column, String, Integer
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
    image_path = Column(String(500), nullable=True)
    image_local_name = Column(String(255), nullable=True)
    image_provider_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<KIImage(id={self.image_id}, name='{self.image_name}', tag='{self.image_tag}')>"


# -----------------------------
# Modell: DICOMMetadata (DICOM-Metadaten)
# -----------------------------
class DICOMMetadata(Base):
    """
    Tabelle 'dicom_metadata' für die Speicherung von DICOM-Metadaten.
    Alle Spalten haben den Prefix 'dicom_'.
    """
    __tablename__ = "dicom_metadata"

    dicom_id = Column(Integer, primary_key=True, index=True)
    dicom_uuid = Column(String(128), unique=True, nullable=False)
    dicom_modality = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<DICOMMetadata(id={self.dicom_id}, uuid='{self.dicom_uuid}', modality='{self.dicom_modality}')>"

