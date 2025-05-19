"""
database.py
-------------
Diese Datei stellt die Verbindung zur Datenbank her und definiert die SessionFactory für SQLAlchemy.
Pfad: backend/src/db/database/database.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv(dotenv_path="./backend/.env")

# Hole die Datenbank-URL aus der Umgebungsvariable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"host": "db"})

# SessionFactory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ⬇️⛓️ Wichtig: Datenbank-Modelle importieren und Tabellen erzeugen
from src.db.db_models.db_models import Base  # Model-Basis
Base.metadata.create_all(bind=engine)
