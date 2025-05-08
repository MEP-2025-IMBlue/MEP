import os
from dotenv import load_dotenv  # Lädt Umgebungsvariablen aus einer .env-Datei
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv(dotenv_path="./backend/.env")

# Hole die Datenbank-URL aus der Umgebungsvariable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Erstelle die SQLAlchemy Engine für die Verbindung zur Datenbank
# Kein zusätzlicher "host"-Parameter notwendig, da Supabase das bereits bereitstellt
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

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
