from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.departments import DepartmentCreate, DepartmentUpdate, FilterDepartmentSearch
from backend.app.services.organization import OrganizationService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class DepartmentsController:
    @staticmethod
    async def create_department(department_data: DepartmentCreate, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            return service.create_department(current_user, department_data)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_departments(filter_params: FilterDepartmentSearch, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            return service.search_departments(current_user, filter_params)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_department_by_id(department_id: int, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            dept = service.get_department_by_id(current_user, department_id)
            if not dept:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department #{department_id} not found")
            return dept
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def update_department(department_id: int, department_data: DepartmentUpdate, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            dept = service.update_department(current_user, department_id, department_data)
            if not dept:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department #{department_id} not found")
            return dept
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
