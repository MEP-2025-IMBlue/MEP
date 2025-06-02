from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from api.py_models.py_models import DICOMMetadata, UploadDICOMResponseModel, UploadResultItem
from db.database.database import get_db
from db.crud import crud_dicom
from db.core.exceptions import *
from src.services.dicom import service_dicom
import shutil, os, uuid, zipfile
import logging

# Logging konfigurieren
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = APIRouter(tags=["DICOM"])

@router.post("/dicoms/uploads", response_model=UploadDICOMResponseModel)
async def post_upload_dicom(file: UploadFile = File(...)):
    try:
        return service_dicom.receive_file(file)
    except DICOMValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DICOMProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unbekannter Fehler: " + str(e))

#TODO: DICOM-Dateien löschen, wenn sie vor X Tagen hochgeladen wurden
@router.delete("/dicoms/uploads/{sop_uid}")
async def delete_upload_dicom(sop_uid):
    try:
        service_dicom.delete_upload_dicom(sop_uid)
        return {"message": f"{sop_uid}_anon.dcm wurde gelöscht"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/dicoms/uploads")
async def get_all_stored_dicom():
    result = service_dicom.get_all_stored_dicom()
    if not result:
        return {"message": "Es wurden noch keine DICOM_Dateien hochgeladen."}
    return result


#TO DO: Post Routen trennen: 1.Post-Route nur Upload, 2.Post-Route (also diese hier) nur Datenbank
@router.post("dicoms/database")

# Liefert eine Liste aller verfügbaren DICOM-Datensätze
@router.get("/dicoms")
async def list_dicoms(db: Session = Depends(get_db)):
    try:
        return crud_dicom.get_all_dicoms(db)
    except NoDICOMInTheList as e:
        logger.warning(f"No DICOMs found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error while listing DICOMs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Gibt einen spezifischen DICOM-Datensatz anhand der ID zurück
@router.get("/dicoms/{dicom_id}", response_model=DICOMMetadata)
async def get_dicom(dicom_id: int, db: Session = Depends(get_db)):
    try:
        return crud_dicom.get_dicom_by_id(db, dicom_id)
    except DICOMNotFound as e:
        logger.warning(f"DICOM not found: ID {dicom_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error while retrieving DICOM {dicom_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Löscht einen DICOM-Datensatz anhand der ID
@router.delete("/dicoms/{dicom_id}")
async def delete_dicom(dicom_id: int, db: Session = Depends(get_db)):
    try:
        deleted_dicom = crud_dicom.delete_dicom(db, dicom_id)
        logger.info(f"DICOM with ID {dicom_id} deleted.")
        return {"message": f"DICOM mit der ID {dicom_id} wurde gelöscht."}
    except DICOMNotFound as e:
        logger.warning(f"Cannot delete DICOM {dicom_id}: Not found")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error while deleting DICOM {dicom_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


