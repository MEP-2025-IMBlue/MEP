# utils.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.db_models.db_models import *
import os
from dotenv import load_dotenv

# .env.test laden
load_dotenv(dotenv_path="./backend/.env.test")
DATABASE_URL = os.getenv("DATABASE_URL")

test_engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseSeeder:
    def __init__(self, session):
        self.session = session

    def populate_test_database(self):
        ki_image_1 = KIImage(
            image_id=300,
            image_name="python",
            image_tag="latest",
            image_provider_id=1,
            image_created_at="240513"
        )
        ki_image_2 = KIImage(
            image_id=200,
            image_name="ubuntu",
            image_tag="latest",
            image_provider_id=1,
            image_created_at="250601"
        )
        self.session.add_all([ki_image_1, ki_image_2])
        self.session.commit()
