from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.darta import CreateDarta, DartaResponse, FilterDartaSearch
from backend.app.controllers.darta import DartaController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/darta", tags=["Darta"])

@router.post("", response_model=DartaResponse)
async def create_darta(
    darta_data: CreateDarta = Depends(CreateDarta.as_form),
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DartaController.create_darta(darta_data, file, current_user, db)

@router.get("", response_model=List[DartaResponse])
async def search_darta(
    filter_params: FilterDartaSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DartaController.search_darta(filter_params, current_user, db)

@router.get("/{darta_id}", response_model=DartaResponse)
async def get_darta_by_id(
    darta_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DartaController.get_darta_by_id(darta_id, current_user, db)

@router.post("/{darta_id}/ocr")
async def run_ocr(
    darta_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DartaController.run_ocr(darta_id, current_user, db)

@router.get("/{darta_id}/download")
async def download_file(
    darta_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DartaController.download_file(darta_id, current_user, db)
