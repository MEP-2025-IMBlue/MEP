from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from api.py_models import py_models
from db.database.database import get_db
from db.crud.crud_dicom import store_dicom_metadata, delete_dicom_metadata, list_dicom_metadata
from db.core.exceptions import *
from services.dicom import service_dicom
from services.dicom.service_dicom import *
import os, logging
import logging


# Logging konfigurieren
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(tags=["DICOM"])

# ========================================
# Upload: Lädt DICOM-Datei in einem temporären Verzeichnis hoch
# TODO: HIER DIE SACHEN von maimuna rein wegen Metadaten Extraktion
# ========================================
@router.post("/dicoms/uploads", response_model=UploadDICOMResponseModel)
async def post_upload_dicom(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        return service_dicom.receive_file(file, db)
    except DICOMValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DICOMProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unbekannter Fehler: " + str(e))

# ========================================
# Upload: Löscht eine bereits hochgeladene DICOM-Datei aus dem temporären Verzeichnis
# ========================================
#TODO: DICOM-Dateien löschen, wenn sie vor X Tagen hochgeladen wurden
@router.delete("/dicoms/uploads/{sop_uid}")
async def delete_upload_dicom(sop_uid):
    try:
        service_dicom.delete_upload_dicom(sop_uid)
        return {"message": f"{sop_uid}_anon.dcm wurde gelöscht"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ========================================
# Upload: Holt eine hochgeladene DICOM-Datei aus dem temporären Verzeichnis
# ========================================

@router.get("/dicoms/uploads")
async def get_all_stored_dicom():
    files = service_dicom.get_all_stored_dicom()
    result = []

    for filename in files:
        if not filename.endswith("_reupload.dcm"):
            continue

        sop_uid = filename.replace("_reupload.dcm", "")
        path = os.path.join(UPLOAD_DIR, filename)
        try:
            modified = os.path.getmtime(path)
            iso_time = datetime.utcfromtimestamp(modified).replace(tzinfo=timezone.utc).isoformat()
        except Exception:
            iso_time = None

        result.append({
            "filename": filename,
            "sop_uid": sop_uid,
            "uploaded_at": iso_time
        })

    return result

@router.get("/dicoms/uploads/{sop_uid}")
async def get_reupload_dicom(sop_uid: str):
    """
    Gibt die gespeicherte Original-Reupload-Datei zurück.
    """
    path = os.path.join(UPLOAD_DIR, f"{sop_uid}_reupload.dcm")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Reupload-Datei nicht gefunden.")
    
    return FileResponse(path, media_type="application/dicom", filename=f"{sop_uid}_reupload.dcm")

# # ========================================
# # TODO: Diese Funktion löschen, nach dem Extraktion der Metadaten in post1 eingegliedert wurde
# # ========================================
# UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")

# async def save_file(upload_file: UploadFile) -> str:
#     """
#     Speichert die hochgeladene Datei temporär und gibt den Dateipfad zurück.
#     """
#     file_path = f"{UPLOAD_DIR}/{upload_file.filename}"
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)
#     with open(file_path, "wb") as f:
#         f.write(upload_file.file.read())
#     return file_path

# ========================================
# Speichert DICOM-Metadaten in der Datenbank
# ========================================
# @router.post("/dicoms/database", response_model=UploadDICOMResponseModel)
# async def upload_dicom_metadata(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     """
#     Lädt eine DICOM-Datei hoch, extrahiert DSGVO-konforme Metadaten und speichert sie in der Datenbank.
    
#     Args:
#         file (UploadFile): Hochgeladene DICOM-Datei.
#         db (Session): SQLAlchemy-Datenbanksitzung.
    
#     Returns:
#         UploadDICOMResponseModel: Status und Ergebnisse der Verarbeitung.
    
#     Raises:
#         HTTPException: Bei ungültigen Dateien oder Datenbankfehlern.
#     """
#     try:
#         # Datei speichern
#         file_path = await save_file(file)
        
#         # DICOM-Datei lesen
#         result = read_dicom(file_path)
#         if result["status"] != "success":
#             return UploadDICOMResponseModel(
#                 message="Fehler bei der Verarbeitung",
#                 data=[UploadResultItem(file=file.filename, error=result["message"])]
#             )
        
#         # Metadaten in der Datenbank speichern
#         db_result = store_dicom_metadata(db, result["metadata"])
#         logging.info(f"[API] DICOM-Metadaten für {file.filename} gespeichert: {db_result}")
        
#         return UploadDICOMResponseModel(
#             message="DICOM-Datei erfolgreich verarbeitet und Metadaten gespeichert.",
#             data=[UploadResultItem(file=file.filename, error=None)]
#         )
    
#     except Exception as e:
#         logging.error(f"[API] Fehler beim Verarbeiten von {file.filename}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Fehler beim Verarbeiten: {str(e)}")
#     finally:
#         # Temporäre Datei löschen (DSGVO-konform)
#         if os.path.exists(file_path):
#             os.remove(file_path)


# ========================================
# Listet DICOM-Metadaten in der Datenbank
# ========================================
@router.get("/dicoms/database", response_model=List[py_models.DICOMMetadata])
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

    # """
    # Listet alle DICOM-Metadatensätze aus der Datenbank und wandelt sie in Pydantic-Modelle um.
    # """
     
    # try:
    #     dicom_metadata = list_dicom_metadata(db)

    #     # Konvertiere jeden SQLAlchemy-Eintrag in ein Pydantic-Modell
    #     pydantic_entries = []
    #     for entry in dicom_metadata:
    #         # Konvertiere datetime in UTC-ISO, falls vorhanden
    #         if hasattr(entry, "dicom_created_at") and entry.dicom_created_at:
    #             entry.dicom_created_at = entry.dicom_created_at.astimezone(timezone.utc).isoformat()
    #         # Wandelt das SQLAlchemy-Modell in ein Pydantic-Modell um
    #         pydantic_entries.append(DICOMMetadata.model_validate(entry))
    #     return pydantic_entries

    # except DatabaseError as e:
    #     logging.error(f"[API] Fehler beim Abrufen der DICOM-Metadatenn: {str(e)}")
    #     raise HTTPException(status_code=500, detail=str(e)) 
    
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
    


