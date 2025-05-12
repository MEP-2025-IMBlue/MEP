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
    image_reference = Column(String(255), nullable=True)
    image_provider_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<KIImage(id={self.image_id}, name='{self.image_name}', tag='{self.image_tag}')>"


# -----------------------------
# Modell: DICOMMetadata (DICOM-Metadaten)
# -----------------------------
class DICOMMetadata(Base):
    """
    Tabelle 'dicom_metadata' für die Speicherung von DICOM-Metadaten.
    """
    __tablename__ = "dicom_metadata"

    dicom_id = Column(Integer, primary_key=True, index=True)
    dicom_uuid = Column(String(64), unique=True, nullable=False)
    dicom_modality = Column(String(50), nullable=True)
    dicom_body_part_examined = Column(String(100), nullable=True)
    dicom_study_description = Column(String(255), nullable=True)
    dicom_model = Column(String(128), nullable=True)

    def __repr__(self):
        return f"<DICOMMetadata(id={self.dicom_id}, uuid='{self.dicom_uuid}')>"
