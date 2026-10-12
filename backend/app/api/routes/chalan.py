from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.chalan import CreateChalan, ChalanResponse, FilterChalanSearch
from backend.app.controllers.chalan import ChalanController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/chalan", tags=["Chalan"])

@router.post("", response_model=ChalanResponse)
async def create_chalan(
    chalan_data: CreateChalan = Depends(CreateChalan.as_form),
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ChalanController.create_chalan(chalan_data, file, current_user, db)

@router.get("", response_model=List[ChalanResponse])
async def search_chalan(
    filter_params: FilterChalanSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ChalanController.search_chalan(filter_params, current_user, db)

@router.get("/{chalan_id}", response_model=ChalanResponse)
async def get_chalan_by_id(
    chalan_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ChalanController.get_chalan_by_id(chalan_id, current_user, db)

@router.post("/{chalan_id}/ocr")
async def run_ocr(
    chalan_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ChalanController.run_ocr(chalan_id, current_user, db)

@router.get("/{chalan_id}/download")
async def download_file(
    chalan_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ChalanController.download_file(chalan_id, current_user, db)
