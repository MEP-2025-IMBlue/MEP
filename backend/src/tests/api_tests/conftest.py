# backend/src/tests/api_tests/conftest.py
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database
from src.db.database.database import get_db
from src.db.db_models.db_models import Base
from src.main import app
import os

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv(dotenv_path="./backend/.env")

# Hole die Datenbank-URL aus der Umgebungsvariable
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

@pytest.fixture(scope="session")
def db_engine():
    if create_database(TEST_DATABASE_URL):  # erzeugt nur, wenn nicht vorhanden
        pass
    create_database(TEST_DATABASE_URL)
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    drop_database(TEST_DATABASE_URL)

@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
