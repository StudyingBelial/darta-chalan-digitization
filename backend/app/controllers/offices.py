from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.offices import OfficeCreate, OfficeUpdate, FilterOfficeSearch
from backend.app.services.organization import OrganizationService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class OfficesController:
    @staticmethod
    async def create_office(office_data: OfficeCreate, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            return service.create_office(current_user, office_data)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_offices(filter_params: FilterOfficeSearch, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            return service.search_offices(current_user, filter_params)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_office_by_id(office_id: int, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            office = service.get_office_by_id(current_user, office_id)
            if not office:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Office #{office_id} not found")
            return office
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def update_office(office_id: int, office_data: OfficeUpdate, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            office = service.update_office(current_user, office_id, office_data)
            if not office:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Office #{office_id} not found")
            return office
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
