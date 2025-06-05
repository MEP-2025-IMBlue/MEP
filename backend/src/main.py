from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Datenbank- und Modellimports
from src.db.database.database import engine
from src.db.db_models import db_models

# Log-System
from src.utils.event_logger import log_event

# API-Routen importieren
from src.api.routes import routes_kiImage
from src.api.routes import routes_kiContainer
from src.api.routes import routes_dicom
from src.api.routes.routes_logsContainer import router as container_logs_router
from src.api.routes.routes_logsFrontend import router as frontend_logs_router

# CORS
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(container_logs_router)
app.include_router(frontend_logs_router)

# Erstelle temporäre Upload-/Verzeichnisse beim Start und logge
@app.on_event("startup")
def prepare_temp_dirs():
    upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    processed_dir = os.getenv("PROCESSED_DIR", "/tmp/processed")
    logs_dir = os.getenv("LOG_DIR", "/tmp/logs")

    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # Logging: Verzeichnisse erfolgreich erstellt
    log_event("System", "startup", "Upload-, Verarbeitungs- und Log-Verzeichnisse wurden erstellt", level="INFO")
    log_event("System", "startup", "mRay AIR Backend wurde erfolgreich gestartet", level="INFO")

# CORS aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
