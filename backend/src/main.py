from fastapi import FastAPI, Depends, HTTPException 
from sqlalchemy.orm import Session
from src.db.crud import crud
from src.db.db_models import db_models
from src.db.database import database
from src.api.routes import KIContainer_routes,KIImage_routes
#-------------------------------------------------------------
# Für die Testverbindung zur DB 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from src.db.database.database import engine

#---------------------------------------------------------------
# Testverbindung zur DB, um sicherzustellen, dass sie funktioniert
#try:
#    with engine.connect() as connection:
#        result = connection.execute(text("SELECT 1"))
#        print("Datenbankverbindung erfolgreich!")
#except Exception as e:
#    print(f"Fehler bei der Verbindung zur Datenbank: {e}")

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