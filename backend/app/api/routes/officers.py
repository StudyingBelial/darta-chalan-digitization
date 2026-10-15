from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.officers import (
    OfficerCreate,
    OfficerUpdate,
    OfficerResponse,
    FilterOfficerSearch,
)
from backend.app.controllers.officers import OfficersController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/officers", tags=["Officers"])

@router.post("", response_model=OfficerResponse)
async def create_officer(
    officer_data: OfficerCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficersController.create_officer(officer_data, current_user, db)

@router.get("", response_model=List[OfficerResponse])
async def get_officers(
    filter_params: FilterOfficerSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficersController.get_officers(filter_params, current_user, db)

@router.get("/{officer_id}", response_model=OfficerResponse)
async def get_officer_by_id(
    officer_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficersController.get_officer_by_id(officer_id, current_user, db)

@router.put("/{officer_id}", response_model=OfficerResponse)
async def update_officer(
    officer_id: int,
    officer_data: OfficerUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficersController.update_officer(officer_id, officer_data, current_user, db)
