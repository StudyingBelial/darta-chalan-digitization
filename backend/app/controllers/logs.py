from sqlalchemy.orm import Session
from backend.app.schemas.logs import FilteredLogSearch
from backend.app.services.system import SystemService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class LogsController:
    @staticmethod
    async def get_logs(filter_params: FilteredLogSearch, current_user: Users, db: Session):
        service = SystemService(db)
        try:
            return service.search_logs(current_user, filter_params)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
