from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from src.api.py_models.py_models import DICOMMetadata
from src.db.database.database import get_db
from src.db.crud import crud_dicom
from src.db.core.exceptions import DICOMNotFound, NoDICOMInTheList
from src.db.core.exceptions import DatabaseError
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.dicom.service_dicom import handle_dicom_upload
import shutil, os, uuid, zipfile

router = APIRouter(tags=["DICOM"])

@router.post("/upload-dicom/")
async def upload_dicom(file: UploadFile = File(...)):
    filename = file.filename.lower()
    tmp_dir = "/tmp/uploads"
    os.makedirs(tmp_dir, exist_ok=True)

    if filename.endswith(".dcm"):
        # Einzelne DICOM-Datei
        tmp_filepath = os.path.join(tmp_dir, f"{uuid.uuid4()}.dcm")
        with open(tmp_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            result = handle_dicom_upload(tmp_filepath)
            return {"message": "Einzelne DICOM-Datei verarbeitet", "data": [result]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler bei Verarbeitung: {str(e)}")

    elif filename.endswith(".zip"):
        # ZIP-Datei mit mehreren DICOMs
        zip_id = str(uuid.uuid4())
        zip_path = os.path.join(tmp_dir, f"{zip_id}.zip")

        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extract_dir = os.path.join(tmp_dir, zip_id)
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Alle DICOMs im entpackten Verzeichnis verarbeiten
        results = []
        for entry in os.listdir(extract_dir):
            if entry.endswith(".dcm"):
                full_path = os.path.join(extract_dir, entry)
                try:
                    result = handle_dicom_upload(full_path)
                    results.append(result)
                except Exception as e:
                    results.append({"file": entry, "error": str(e)})

        return {"message": "ZIP-Datei verarbeitet", "data": results}

    else:
        raise HTTPException(status_code=400, detail="Nur .dcm oder .zip-Dateien erlaubt.")
    
# async def add_dicom(dicom: DICOMMetadata, db: Session = Depends(get_db)):
#     try:
#         dicom_data_dict = dicom.model_dump(exclude_unset=True)
#         return crud_dicom.create_dicom(db, dicom_data_dict)
#     except DatabaseError as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/dicoms")
async def list_dicoms(db: Session = Depends(get_db)):
    try:
        return crud_dicom.get_all_dicoms(db)
    except NoDICOMInTheList as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dicoms/{dicom_id}", response_model=DICOMMetadata)
async def get_dicom(dicom_id: int, db: Session = Depends(get_db)):
    try:
        return crud_dicom.get_dicom_by_id(db, dicom_id)
    except DICOMNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/dicoms/{dicom_id}", response_model=DICOMMetadata)
async def patch_dicom(dicom_id: int, updated_dicom: DICOMMetadata, db: Session = Depends(get_db)):
    try:
        update_data = updated_dicom.model_dump(exclude_unset=True)
        return crud_dicom.update_dicom(db, dicom_id, update_data)
    except DICOMNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/dicoms/{dicom_id}")
async def delete_dicom(dicom_id: int, db: Session = Depends(get_db)):
    try:
        deleted_dicom = crud_dicom.delete_dicom(db, dicom_id)
        return {"message": f"DICOM mit der ID {dicom_id} wurde gelöscht."}
    except DICOMNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
