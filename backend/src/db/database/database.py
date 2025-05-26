"""
database.py
-------------
Diese Datei stellt die Verbindung zur Datenbank her und definiert die SessionFactory für SQLAlchemy.
Pfad: backend/src/database/database.py
"""
import os
from dotenv import load_dotenv  # Lädt Umgebungsvariablen aus einer .env-Datei
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv(dotenv_path="./backend/.env")

# Hole die Datenbank-URL aus der Umgebungsvariable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Erstelle die SQLAlchemy Engine für die Verbindung zur Datenbank
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Erstelle eine SessionFactory (SessionLocal), um Sessions mit der DB zu erzeugen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency, die eine DB-Session bereitstellt und nach der Verwendung wieder schließt.
    Verwendung in FastAPI mit: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

