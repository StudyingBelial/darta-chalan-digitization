from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.financial_year import FinancialYearCreate, FinancialYearUpdate, FilterFinancialYearSearch
from backend.app.services.system import SystemService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class FinancialYearController:
    @staticmethod
    async def create_financial_year(fy_data: FinancialYearCreate, current_user: Users, db: Session):
        service = SystemService(db)
        try:
            return service.create_financial_year(current_user, fy_data)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_financial_years(filter_params: FilterFinancialYearSearch, current_user: Users, db: Session):
        service = SystemService(db)
        try:
            return service.search_financial_years(current_user, filter_params)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_financial_year_by_id(fy_id: int, current_user: Users, db: Session):
        service = SystemService(db)
        try:
            fy = service.get_financial_year_by_id(current_user, fy_id)
            if not fy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Financial Year #{fy_id} not found")
            return fy
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def update_financial_year(fy_id: int, fy_data: FinancialYearUpdate, current_user: Users, db: Session):
        service = SystemService(db)
        try:
            fy = service.update_financial_year(current_user, fy_id, fy_data)
            if not fy:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Financial Year #{fy_id} not found")
            return fy
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
