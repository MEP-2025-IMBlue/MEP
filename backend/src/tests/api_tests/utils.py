"""utils.py is a special file where we’ll store additional functions and database population"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from db.db_models.db_models import *
from tests.api_tests.fixtures import TEST_DATABASE_URL

class TestDatabase:
    def __init__(self, session: Session):
        self.session = session
        
    def populate_test_database(self):
        ki_image_1 = KIImage(
            name="Product 2",
            quantity=10
        )
        
        ki_image_2 = KIImage(
            name="Product 1",
            quantity=4
        )
        
        ki_image_3 = KIImage(
            name="Product 3",
            quantity=84
        )
        
        self.session.add_all([ki_image_1, ki_image_2, ki_image_3])
        self.session.commit()

def override_get_db():
    test_engine = create_engine(TEST_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()