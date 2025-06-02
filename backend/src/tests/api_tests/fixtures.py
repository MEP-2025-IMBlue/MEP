"""fixtures.py – Stellt Test-Datenbank und Session zur Verfügung"""

import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database, database_exists

from src.db.db_models import db_models
from src.tests.api_tests.utils import DatabaseSeeder

# Lade .env.test
load_dotenv(dotenv_path="./backend/.env.test")

# Hole Test-URL
TEST_DATABASE_URL = "postgresql://imblue_user:secret@localhost:5432/TEST"

# Erzeuge globale Engine und SessionLocal für Tests
test_engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Erstellt die Test-Datenbank und füllt sie vor Tests"""
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    create_database(TEST_DATABASE_URL)

    # Tabellen erzeugen
    db_models.Base.metadata.create_all(test_engine)

    # Testdaten einfügen
    session = SessionLocal()
    DatabaseSeeder(session=session).populate_test_database()
    session.close()

    yield  # hier laufen die Tests

    # Danach: Datenbank löschen
    drop_database(TEST_DATABASE_URL)