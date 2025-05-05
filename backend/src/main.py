from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy.orm import Session
from src.db.crud import crud
from src.db.db_models import db_models
from src.db.database import database
from src.api.routes import KIContainer_routes,KIImage_routes 

# ------------------------------------------------------------
# Erstelle die FastAPI-Anwendung
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome"} 

# ------------------------------------------------------------
# Initialisiere die Datenbank: Erstelle alle Tabellen, falls sie nicht existieren
db_models.Base.metadata.create_all(bind=database.engine)

# ------------------------------------------------------------
# Binde die API-Routen an die FastAPI-Anwendung
app.include_router(KIImage_routes.router)
app.include_router(KIContainer_routes.router)