from sqlalchemy.orm import Session
from fastapi import Response
from backend.app.schemas.darta import FilterDartaSearch
from backend.app.schemas.chalan import FilterChalanSearch
from backend.app.services.export_service import ExportService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class ExportController:
    @staticmethod
    async def export_darta_csv(filter_params: FilterDartaSearch, current_user: Users, db: Session):
        service = ExportService(db)
        try:
            csv_content = service.export_darta_register_csv(
                user=current_user,
                receiver_office=filter_params.receiver_office,
                financial_year_id=filter_params.financial_year,
                start_date_bs=filter_params.from_date_bs,
                end_date_bs=filter_params.to_date_bs
            )
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=darta_register.csv"}
            )
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def export_chalan_csv(filter_params: FilterChalanSearch, current_user: Users, db: Session):
        service = ExportService(db)
        try:
            csv_content = service.export_chalan_register_csv(
                user=current_user,
                sender_office=filter_params.sender_office,
                start_date_bs=filter_params.from_date_bs,
                end_date_bs=filter_params.to_date_bs
            )
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=chalan_register.csv"}
            )
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
