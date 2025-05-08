from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.api.py_models.py_models import DICOMMetadata
from src.db.database.database import get_db
from src.db.crud import crud_dicom
from src.db.core.exceptions import DICOMNotFound, NoDICOMInTheList
from src.db.core.exceptions import DatabaseError

router = APIRouter(tags=["DICOM"])

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

@router.post("/dicoms", response_model=DICOMMetadata)
async def add_dicom(dicom: DICOMMetadata, db: Session = Depends(get_db)):
    try:
        dicom_data_dict = dicom.model_dump(exclude_unset=True)
        return crud_dicom.create_dicom(db, dicom_data_dict)
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
