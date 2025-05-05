# Importiere notwendige Module
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Dies ist die Basisklasse für alle Modelle. Alle Tabellen erben von dieser Klasse.
Base = declarative_base()

# Definition des KI-Image-Modells, das die Tabelle "ki_image_metadata" abbildet
class KIImage(Base):
    """
    Tabelle 'ki_image_metadata' für die Speicherung von KI-Image-Metadaten
    """
    __tablename__ = 'ki_image_metadata'  # Name der Tabelle in der DB

    # Spalten der Tabelle
    image_id = Column(int, primary_key=True)
    image_name = Column(String(255), nullable=False)
    image_tag = Column(String(128), nullable=False)
    description = Column(String(255), nullable=True)
    image_path = Column(String(255), nullable=True)
    local_image_name = Column(String(255), nullable=True) 
    provider_id = Column(int(32), nullable=False)

    # Repräsentation des Modells als String
    def __repr__(self):
        return f"<KIImage(image_id={self.image_id}, image_name={self.image_name})>"
