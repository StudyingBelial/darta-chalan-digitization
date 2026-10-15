from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.offices import (
    OfficeCreate,
    OfficeUpdate,
    OfficeResponse,
    FilterOfficeSearch,
)
from backend.app.controllers.offices import OfficesController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/offices", tags=["Offices"])

@router.post("", response_model=OfficeResponse)
async def create_office(
    office_data: OfficeCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficesController.create_office(office_data, current_user, db)

@router.get("", response_model=List[OfficeResponse])
async def get_offices(
    filter_params: FilterOfficeSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficesController.get_offices(filter_params, current_user, db)

@router.get("/{office_id}", response_model=OfficeResponse)
async def get_office_by_id(
    office_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficesController.get_office_by_id(office_id, current_user, db)

@router.put("/{office_id}", response_model=OfficeResponse)
async def update_office(
    office_id: int,
    office_data: OfficeUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await OfficesController.update_office(office_id, office_data, current_user, db)
