import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importiere das Datenbankmodell und die zu testenden CRUD-Funktionen
from src.db.db_models.db_models import Base, KIImage
from src.db.crud.crud_kiImage import (
    create_ki_image,
    get_ki_image_by_id,
    get_all_ki_images,
    update_ki_image,
    delete_ki_image,
)
from src.db.core.exceptions import KIImageNotFound, NoKIImagesInTheList

# ➤ FIXTURE: Erstellt eine temporäre SQLite-Datenbank im RAM, die für jeden Test neu aufgesetzt wird
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# ➤ Test: Erstellen eines neuen KIImage-Eintrags
def test_create_ki_image(db_session):
    data = {"image_name": "TestImage", "image_tag": "v1", "image_provider_id": 1}
    image = create_ki_image(db_session, data)
    assert image.image_name == "TestImage"
    assert image.image_tag == "v1"
    assert image.image_provider_id == 1

# ➤ Test: Ein einzelnes KIImage per ID abrufen (Erfolgsfall)
def test_get_ki_image_by_id_success(db_session):
    image = create_ki_image(db_session, {"image_name": "TestImage", "image_tag": "v1", "image_provider_id": 1})
    result = get_ki_image_by_id(db_session, image.image_id)
    assert result.image_id == image.image_id

# ➤ Test: Fehlerfall – Kein KIImage mit der gegebenen ID vorhanden
def test_get_ki_image_by_id_not_found(db_session):
    with pytest.raises(KIImageNotFound):
        get_ki_image_by_id(db_session, 999)

# ➤ Test: Fehlerfall – Leere Liste von KIImages
def test_get_all_ki_images_empty(db_session):
    with pytest.raises(NoKIImagesInTheList):
        get_all_ki_images(db_session)

# ➤ Test: Erfolgreiches Abrufen einer Liste mit mindestens einem KIImage
def test_get_all_ki_images_with_data(db_session):
    create_ki_image(db_session, {"image_name": "A", "image_tag": "1", "image_provider_id": 1})
    images = get_all_ki_images(db_session)
    assert len(images) == 1

# ➤ Test: Erfolgreiches Aktualisieren eines KIImage
def test_update_ki_image_success(db_session):
    image = create_ki_image(db_session, {"image_name": "Old", "image_tag": "v1", "image_provider_id": 1})
    updated = update_ki_image(db_session, image.image_id, {"image_name": "New"})
    assert updated.image_name == "New"

# ➤ Test: Fehlerfall – Update mit ungültiger ID
def test_update_ki_image_not_found(db_session):
    with pytest.raises(KIImageNotFound):
        update_ki_image(db_session, 123, {"image_name": "Fail"})

# ➤ Test: Erfolgreiches Löschen eines KIImage
def test_delete_ki_image_success(db_session):
    image = create_ki_image(db_session, {"image_name": "DeleteMe", "image_tag": "v1", "image_provider_id": 1})
    deleted = delete_ki_image(db_session, image.image_id)
    assert deleted.image_id == image.image_id

# ➤ Test: Fehlerfall – Löschen mit ungültiger ID
def test_delete_ki_image_not_found(db_session):
    with pytest.raises(KIImageNotFound):
        delete_ki_image(db_session, 999)
