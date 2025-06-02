from datetime import timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from api.py_models.py_models import DICOMMetadata, UploadDICOMResponseModel, UploadResultItem
from db.database.database import get_db
from db.crud.crud_dicom import store_dicom_metadata, delete_dicom_metadata, list_dicom_metadata
from db.core.exceptions import DICOMNotFound, DatabaseError
from services.dicom.service_dicom import read_dicom
import os, logging

# Logging konfigurieren
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(tags=["DICOM"])

# ========================================
# Speichert DICOM-Datei Temporär ab
# ========================================
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")

async def save_file(upload_file: UploadFile) -> str:
    """
    Speichert die hochgeladene Datei temporär und gibt den Dateipfad zurück.
    """
    file_path = f"{UPLOAD_DIR}/{upload_file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path

# ========================================
# Speichert DICOM-Metadaten in der Datenbank
# ========================================
@router.post("/dicoms/database", response_model=UploadDICOMResponseModel)
async def upload_dicom(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Lädt eine DICOM-Datei hoch, extrahiert DSGVO-konforme Metadaten und speichert sie in der Datenbank.
    
    Args:
        file (UploadFile): Hochgeladene DICOM-Datei.
        db (Session): SQLAlchemy-Datenbanksitzung.
    
    Returns:
        UploadDICOMResponseModel: Status und Ergebnisse der Verarbeitung.
    
    Raises:
        HTTPException: Bei ungültigen Dateien oder Datenbankfehlern.
    """
    try:
        # Datei speichern
        file_path = await save_file(file)
        
        # DICOM-Datei lesen
        result = read_dicom(file_path)
        if result["status"] != "success":
            return UploadDICOMResponseModel(
                message="Fehler bei der Verarbeitung",
                data=[UploadResultItem(file=file.filename, error=result["message"])]
            )
        
        # Metadaten in der Datenbank speichern
        db_result = store_dicom_metadata(db, result["metadata"])
        logging.info(f"[API] DICOM-Metadaten für {file.filename} gespeichert: {db_result}")
        
        return UploadDICOMResponseModel(
            message="DICOM-Datei erfolgreich verarbeitet und Metadaten gespeichert.",
            data=[UploadResultItem(file=file.filename, error=None)]
        )
    
    except Exception as e:
        logging.error(f"[API] Fehler beim Verarbeiten von {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Verarbeiten: {str(e)}")
    finally:
        # Temporäre Datei löschen (DSGVO-konform)
        if os.path.exists(file_path):
            os.remove(file_path)

# ========================================
# Listet DICOM-Metadaten in der Datenbank
# ========================================
@router.get("/dicoms/database", response_model=List[DICOMMetadata])
async def list_dicoms(db: Session = Depends(get_db)):
    """
    Listet alle DICOM-Metadatensätze aus der Datenbank.
    
    Args:
        db (Session): SQLAlchemy-Datenbanksitzung.
    
    Returns:
        List[DICOMMetadata]: Liste aller DICOM-Metadatensätze.
    
    Raises:
        HTTPException: Bei Datenbankfehlern.
    """
    try:
        dicom_metadata = list_dicom_metadata(db)

        # Konvertiere dicom_created_at zu UTC mit ISO-Format
        for dicom in dicom_metadata:
            dicom.dicom_created_at = dicom.dicom_created_at.astimezone(timezone.utc).isoformat()
 
        return dicom_metadata
    except DatabaseError as e:
        logging.error(f"[API] Fehler beim Abrufen der DICOM-Metadaten: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ========================================
# Löscht DICOM-Metadaten in der Datenbank
# ========================================
@router.delete("/dicoms/database/{dicom_id}", response_model=dict)
async def delete_dicom(dicom_id: int, db: Session = Depends(get_db)):
    """
    Löscht einen DICOM-Metadatensatz anhand der dicom_id.
    
    Args:
        dicom_id (int): ID des zu löschenden DICOM-Eintrags.
        db (Session): SQLAlchemy-Datenbanksitzung.
    
    Returns:
        dict: Status und Nachricht zur Löschung.
    
    Raises:
        HTTPException: Bei ungültiger ID oder Datenbankfehlern.
    """
    try:
        deleted = delete_dicom_metadata(db, dicom_id)
        if deleted:
            logging.info(f"[API] DICOM-Eintrag mit ID {dicom_id} gelöscht.")
            return {"status": "success", "message": f"DICOM-Eintrag mit ID {dicom_id} gelöscht."}
    except DICOMNotFound as e:
        logging.error(f"[API] Fehler beim Löschen: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logging.error(f"[API] Fehler beim Löschen: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ========================================
# Vorherige Funktionen
# ========================================

#TO DO: Funktionen besser auslagern, die Route macht keine Logik, nur HTTPException Handling
# Upload-Endpunkt für einzelne DICOM-Dateien oder ZIP-Archive
# @router.post("/dicoms", response_model=UploadDICOMResponseModel)
# async def upload_dicom(file: UploadFile = File(...)):
#     filename = file.filename.lower()
#     os.makedirs(UPLOAD_DIR, exist_ok=True)

#     if filename.endswith(".dcm"):
#         tmp_filepath = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.dcm")
#         try:
#             with open(tmp_filepath, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
#             result = handle_dicom_upload(tmp_filepath)
#             logger.info(f"Successfully uploaded single DICOM file: {filename}")
#             return UploadDICOMResponseModel(
#                 message="Einzelne DICOM-Datei verarbeitet",
#                 data=[UploadResultItem(**result)]
#             )
#         except Exception as e:
#             logger.error(f"Error processing single DICOM file: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Fehler bei Verarbeitung: {str(e)}")
#         finally:
#             if os.path.exists(tmp_filepath):
#                 os.remove(tmp_filepath)  # 🧹 Temporäre Datei löschen

#     elif filename.endswith(".zip"):
#         zip_id = str(uuid.uuid4())
#         zip_path = os.path.join(UPLOAD_DIR, f"{zip_id}.zip")
#         extract_dir = os.path.join(UPLOAD_DIR, zip_id)
#         results = []

#         try:
#             with open(zip_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)

#             os.makedirs(extract_dir, exist_ok=True)
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(extract_dir)

#             for root, dirs, files in os.walk(extract_dir):  # 🔁 ZIP rekursiv verarbeiten
#                 for entry in files:
#                     if entry.endswith(".dcm"):
#                         full_path = os.path.join(root, entry)
#                         try:
#                             result = handle_dicom_upload(full_path)
#                             logger.info(f"Successfully processed DICOM from ZIP: {entry}")
#                             results.append(UploadResultItem(**result))
#                         except Exception as e:
#                             logger.error(f"Error while processing file from ZIP: {entry} → {str(e)}")
#                             results.append(UploadResultItem(file=entry, error=str(e)))

#             return UploadDICOMResponseModel(
#                 message="ZIP-Datei verarbeitet",
#                 data=results
#             )
#         except Exception as e:
#             logger.error(f"Unhandled exception during ZIP processing: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Fehler bei ZIP-Verarbeitung: {str(e)}")
#         finally:
#             # 🧹 Temporäre ZIP-Datei und extrahiertes Verzeichnis löschen
#             if os.path.exists(zip_path):
#                 os.remove(zip_path)
#             if os.path.exists(extract_dir):
#                 shutil.rmtree(extract_dir, ignore_errors=True)

#     else:
#         logger.warning(f"Invalid file type uploaded: {filename}")
#         raise HTTPException(status_code=400, detail="Nur .dcm oder .zip-Dateien erlaubt.")

# Liefert eine Liste aller verfügbaren DICOM-Datensätze
# @router.get("/dicoms")
# async def list_dicoms(db: Session = Depends(get_db)):
#     try:
#         return crud_dicom.get_all_dicoms(db)
#     except NoDICOMInTheList as e:
#         logger.warning(f"No DICOMs found: {str(e)}")
#         raise HTTPException(status_code=404, detail=str(e))
#     except DatabaseError as e:
#         logger.error(f"Database error while listing DICOMs: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# Gibt einen spezifischen DICOM-Datensatz anhand der ID zurück
# @router.get("/dicoms/{dicom_id}", response_model=DICOMMetadata)
# async def get_dicom(dicom_id: int, db: Session = Depends(get_db)):
#     try:
#         return crud_dicom.get_dicom_by_id(db, dicom_id)
#     except DICOMNotFound as e:
#         logger.warning(f"DICOM not found: ID {dicom_id}")
#         raise HTTPException(status_code=404, detail=str(e))
#     except DatabaseError as e:
#         logger.error(f"Database error while retrieving DICOM {dicom_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# Löscht einen DICOM-Datensatz anhand der ID
# @router.delete("/dicoms/{dicom_id}")
# async def delete_dicom(dicom_id: int, db: Session = Depends(get_db)):
#     try:
#         deleted_dicom = crud_dicom.delete_dicom(db, dicom_id)
#         logger.info(f"DICOM with ID {dicom_id} deleted.")
#         return {"message": f"DICOM mit der ID {dicom_id} wurde gelöscht."}
#     except DICOMNotFound as e:
#         logger.warning(f"Cannot delete DICOM {dicom_id}: Not found")
#         raise HTTPException(status_code=404, detail=str(e))
#     except DatabaseError as e:
#         logger.error(f"Database error while deleting DICOM {dicom_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


