from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.financial_year import (
    FinancialYearCreate,
    FinancialYearUpdate,
    FinancialYearResponse,
    FilterFinancialYearSearch,
)
from backend.app.controllers.financial_year import FinancialYearController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/financial-years", tags=["Financial Years"])

@router.post("", response_model=FinancialYearResponse)
async def create_financial_year(
    fy_data: FinancialYearCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await FinancialYearController.create_financial_year(fy_data, current_user, db)

@router.get("", response_model=List[FinancialYearResponse])
async def get_financial_years(
    filter_params: FilterFinancialYearSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await FinancialYearController.get_financial_years(filter_params, current_user, db)

@router.get("/{fy_id}", response_model=FinancialYearResponse)
async def get_financial_year_by_id(
    fy_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await FinancialYearController.get_financial_year_by_id(fy_id, current_user, db)

@router.put("/{fy_id}", response_model=FinancialYearResponse)
async def update_financial_year(
    fy_id: int,
    fy_data: FinancialYearUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await FinancialYearController.update_financial_year(fy_id, fy_data, current_user, db)
