from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.departments import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    FilterDepartmentSearch,
)
from backend.app.controllers.departments import DepartmentsController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DepartmentsController.create_department(department_data, current_user, db)

@router.get("", response_model=List[DepartmentResponse])
async def get_departments(
    filter_params: FilterDepartmentSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DepartmentsController.get_departments(filter_params, current_user, db)

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department_by_id(
    department_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DepartmentsController.get_department_by_id(department_id, current_user, db)

@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await DepartmentsController.update_department(department_id, department_data, current_user, db)
