import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
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
    image_reference = Column(String(255), nullable=True)
    image_provider_id = Column(Integer, nullable=False)
    image_created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    image_modality = Column(String(128), nullable=True) #TODO Datentyp entscheiden
    image_bodypart = Column(String(128), nullable=True) #TODO Datentyp entscheiden
    image_purpose = Column(String(128), nullable=True) #TODO Datentyp entscheiden
    image_description = Column(String(500), nullable=True)

    # Beziehung zur ContainerConfiguration-Tabelle (optional, für JOIN-Zugriffe)
    container_configs = relationship("ContainerConfiguration", back_populates="ki_image")


    def __repr__(self):
        return f"<KIImage(id={self.image_id}, name='{self.image_name}', tag='{self.image_tag}')>"
    
# -----------------------------
# Modell: ContainerConfiguration 
# -----------------------------
class ContainerConfiguration(Base):
    """
    Tabelle 'container_configs' zur Speicherung der Container-Konfigurationen eines KI-Images.
    """
    __tablename__ = "container_configuration"

    config_id = Column(Integer, primary_key=True, index=True)
    ki_image_id = Column(Integer, ForeignKey("ki_image_metadata.image_id"), nullable=False)

    input_format = Column(String(50), nullable=False)
    input_dir = Column(String(255), nullable=False)
    output_dir = Column(String(255), nullable=False)
    output_format = Column(String(50), nullable=True)
    environment = Column(JSON, nullable=True) #TODO: Datentyp validieren
    run_command = Column(String(255), nullable=True)
    working_dir = Column(String(255), nullable=True)
    volumes = Column(JSON, nullable=True)
    entrypoint = Column(String(255), nullable=True)
    gpu_required = Column(Boolean, nullable=True)

    # Beziehung zur KIImage-Tabelle (optional, für JOIN-Zugriffe)
    ki_image = relationship("KIImage", back_populates="container_configs")


    def __repr__(self):
        return f"<ContainerConfiguration(id={self.id}, ki_image_id='{self.ki_image_id}')>"

# -----------------------------
# Modell: DICOMMetadata (DICOM-Metadaten)
# -----------------------------
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
    

