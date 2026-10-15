from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.officers import OfficerCreate, OfficerUpdate, FilterOfficerSearch
from backend.app.services.organization import OrganizationService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class OfficersController:
    @staticmethod
    async def create_officer(officer_data: OfficerCreate, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            return service.create_officer(current_user, officer_data)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_officers(filter_params: FilterOfficerSearch, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            return service.search_officers(current_user, filter_params)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_officer_by_id(officer_id: int, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            officer = service.get_officer_by_id(current_user, officer_id)
            if not officer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Officer #{officer_id} not found")
            return officer
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def update_officer(officer_id: int, officer_data: OfficerUpdate, current_user: Users, db: Session):
        service = OrganizationService(db)
        try:
            officer = service.update_officer(current_user, officer_id, officer_data)
            if not officer:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Officer #{officer_id} not found")
            return officer
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
