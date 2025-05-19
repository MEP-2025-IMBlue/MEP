
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()
from db.database.database import engine
# SQLAlchemy & Datenbank

from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy.orm import Session
from src.api.routes import routes_kiImage
from src.db.crud import crud_kiImage
from src.db.db_models import db_models
from src.db.database import database
from src.api.routes import routes_kiContainer
from fastapi.middleware.cors import CORSMiddleware
#-------------------------------------------------------------
# Für die Testverbindung zur DB 

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from db.db_models import db_models
from db.database import database
from db.database.database import engine  # 

# API-Routen importieren
from api.routes import routes_kiImage
from api.routes import routes_kiContainer
from api.routes import routes_dicom

# FastAPI-App instanzieren
app = FastAPI(
    title="mRay AIR Backend",
    version="1.0.0",
    description="Container- & DICOM-Upload Backend mit FastAPI"
)

# Root-Endpunkt
@app.get("/")
def root():
    return {"message": "Welcome to mRay AIR Backend!"}

# Datenbanktabellen initialisieren (nur beim ersten Start)
db_models.Base.metadata.create_all(bind=engine)

# Routen einbinden
app.include_router(routes_kiImage.router)
app.include_router(routes_kiContainer.router)

app.include_router(routes_dicom.router)

# Erstelle bei Anwendungstart temporäre Upload-Verzeichnisse
@app.on_event("startup")
def prepare_temp_dirs():
    upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    processed_dir = os.getenv("PROCESSED_DIR", "/tmp/processed")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für lokale Entwicklung
    allow_methods=["*"],
    allow_headers=["*"],
)

