import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importiere Datenbankmodell und CRUD-Funktionen
from src.db.db_models.db_models import Base, DICOMMetadata
from src.db.crud.crud_dicom import (
    create_dicom,
    get_dicom_metadata_by_uuid,
    update_dicom_metadata,
    delete_dicom_metadata,
    create_or_replace_dicom_metadata,
)
from src.db.core.exceptions import DICOMNotFound, DatabaseError

# ➤ In-Memory SQLite-DB für jeden Test neu erzeugen
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

# ➤ Test: Erstellen eines DICOM-Eintrags
def test_create_dicom(db_session):
    data = {"dicom_uuid": "uuid-123", "dicom_modality": "CT"}
    entry = create_dicom(db_session, data)
    assert entry.dicom_uuid == "uuid-123"
    assert entry.dicom_modality == "CT"

# ➤ Test: Abrufen per UUID (erfolgreich)
def test_get_dicom_metadata_by_uuid_success(db_session):
    create_dicom(db_session, {"dicom_uuid": "uuid-456", "dicom_modality": "MRI"})
    entry = get_dicom_metadata_by_uuid(db_session, "uuid-456")
    assert entry.dicom_modality == "MRI"

# ➤ Test: Fehler – UUID nicht vorhanden
def test_get_dicom_metadata_by_uuid_not_found(db_session):
    with pytest.raises(DICOMNotFound):
        get_dicom_metadata_by_uuid(db_session, "nonexistent")

# ➤ Test: Aktualisieren eines bestehenden Eintrags
def test_update_dicom_metadata_success(db_session):
    create_dicom(db_session, {"dicom_uuid": "uuid-789", "dicom_modality": "PET"})
    updated = update_dicom_metadata(db_session, "uuid-789", {"dicom_modality": "XRAY"})
    assert updated.dicom_modality == "XRAY"

# ➤ Test: Fehler – Update mit ungültiger UUID
def test_update_dicom_metadata_not_found(db_session):
    with pytest.raises(DICOMNotFound):
        update_dicom_metadata(db_session, "invalid-uuid", {"dicom_modality": "X"})

# ➤ Test: Löschen eines Eintrags
def test_delete_dicom_metadata_success(db_session):
    create_dicom(db_session, {"dicom_uuid": "uuid-del", "dicom_modality": "CT"})
    result = delete_dicom_metadata(db_session, "uuid-del")
    assert result is True

# ➤ Test: Fehler – Löschen mit ungültiger UUID
def test_delete_dicom_metadata_not_found(db_session):
    with pytest.raises(DICOMNotFound):
        delete_dicom_metadata(db_session, "not-found")

# ➤ Test: create_or_replace ersetzt vorhandenen Eintrag
def test_create_or_replace_dicom_metadata_replace(db_session):
    create_dicom(db_session, {"dicom_uuid": "uuid-replace", "dicom_modality": "PET"})
    replaced = create_or_replace_dicom_metadata(db_session, {"dicom_uuid": "uuid-replace", "dicom_modality": "XRAY"})
    assert replaced.dicom_modality == "XRAY"

# ➤ Test: create_or_replace legt neuen Eintrag an
def test_create_or_replace_dicom_metadata_new(db_session):
    created = create_or_replace_dicom_metadata(db_session, {"dicom_uuid": "uuid-new", "dicom_modality": "US"})
    assert created.dicom_uuid == "uuid-new"
