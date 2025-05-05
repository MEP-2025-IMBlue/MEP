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
    image_id = Column(String, primary_key=True)
    image_name = Column(String(255), nullable=False)
    tag = Column(String(128), nullable=False)
    repository = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    size = Column(Integer, nullable=False)
    architecture = Column(String(32))
    os = Column(String(32))

    # Repräsentation des Modells als String
    def __repr__(self):
        return f"<KIImage(image_id={self.image_id}, image_name={self.image_name})>"
