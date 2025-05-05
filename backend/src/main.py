from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy.orm import Session
from src.db.crud import crud
from src.db.db_models import db_models
from src.db.database import database
from backend.src.api.routes import KIImage_routes as router

# ------------------------------------------------------------
# Erstelle die FastAPI-Anwendung
app = FastAPI()

# ------------------------------------------------------------
# Initialisiere die Datenbank: Erstelle alle Tabellen, falls sie nicht existieren
db_models.Base.metadata.create_all(bind=database.engine)

# ------------------------------------------------------------
# Binde die API-Routen an die FastAPI-Anwendung
app.include_router(router)
