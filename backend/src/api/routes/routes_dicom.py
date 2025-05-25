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

#TODO: Funktionen besser auslagern, die Route macht keine Logik, nur HTTPException Handling
# + neue Route zum Löschen der temporär gespeciehrten Datei
# Upload-Endpunkt für einzelne DICOM-Dateien oder ZIP-Archive
@router.post("/dicoms", response_model=UploadDICOMResponseModel)
async def post_upload_dicom(file: UploadFile = File(...)):
    try:
        return service_dicom.receive_file(file)
    except DICOMValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DICOMProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unbekannter Fehler: " + str(e))

 
    
    
    #ALLES AB HIER BURAK ORIGINAL
    # filename = file.filename.lower()
    # os.makedirs(UPLOAD_DIR, exist_ok=True)

    #if filename.endswith(".dcm"):
        tmp_filepath = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.dcm")
        try:
            with open(tmp_filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            result = handle_dicom_upload(tmp_filepath)
            logger.info(f"Successfully uploaded single DICOM file: {filename}")
            return UploadDICOMResponseModel(
                message="Einzelne DICOM-Datei verarbeitet",
                data=[UploadResultItem(**result)]
            )
        except Exception as e:
            logger.error(f"Error processing single DICOM file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Fehler bei Verarbeitung: {str(e)}")
        finally:
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)  # 🧹 Temporäre Datei löschen

    #elif filename.endswith(".zip"):
        zip_id = str(uuid.uuid4())
        zip_path = os.path.join(UPLOAD_DIR, f"{zip_id}.zip")
        extract_dir = os.path.join(UPLOAD_DIR, zip_id)
        results = []

        try:
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            for root, dirs, files in os.walk(extract_dir):  # 🔁 ZIP rekursiv verarbeiten
                for entry in files:
                    if entry.endswith(".dcm"):
                        full_path = os.path.join(root, entry)
                        try:
                            result = handle_dicom_upload(full_path)
                            logger.info(f"Successfully processed DICOM from ZIP: {entry}")
                            results.append(UploadResultItem(**result))
                        except Exception as e:
                            logger.error(f"Error while processing file from ZIP: {entry} → {str(e)}")
                            results.append(UploadResultItem(file=entry, error=str(e)))

            return UploadDICOMResponseModel(
                message="ZIP-Datei verarbeitet",
                data=results
            )
        except Exception as e:
            logger.error(f"Unhandled exception during ZIP processing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Fehler bei ZIP-Verarbeitung: {str(e)}")
        finally:
            # 🧹 Temporäre ZIP-Datei und extrahiertes Verzeichnis löschen
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)

    # else:
    #     logger.warning(f"Invalid file type uploaded: {filename}")
    #     raise HTTPException(status_code=400, detail="Nur .dcm oder .zip-Dateien erlaubt.")

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


