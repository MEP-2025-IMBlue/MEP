"""fixtures.py contains fixtures used for our test cases. 
In testing, a fixture provides a defined, reliable and consistent context for the tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions
from sqlalchemy_utils import create_database, drop_database, database_exists

from database import Base
from tests.api_tests.utils import TestDatabase

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/TEST"
fixture_used = False
@pytest.fixture(scope="session", autouse=True)
def create_and_delete_database():
    global fixture_used
    if fixture_used:
        yield
        return
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    create_database(TEST_DATABASE_URL)
    test_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    TestDatabase(session=SessionLocal()).populate_test_database()
    fixture_used = True
    yield
    close_all_sessions()
    drop_database(TEST_DATABASE_URL)