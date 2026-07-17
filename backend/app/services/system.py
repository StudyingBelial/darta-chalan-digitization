from sqlalchemy.orm import Session
from backend.app.db.models.users import Users
from backend.app.db.models.financial_year import FinancialYear
from backend.app.db.models.logs import Logs
from backend.app.enums import PERMISSIONS
from backend.app.core.permissions import has_permission

from backend.app.schemas import (
    FinancialYearCreate,
    FinancialYearUpdate,
    FilterFinancialYearSearch,
    CreateLogs,
    FilteredLogSearch
)

from backend.app.repositories import FinancialYearRepository, LogRepository

class SystemService:
    def __init__(self, db: Session):
        self.db = db
        self.financial_year_repo = FinancialYearRepository(db)
        self.log_repo = LogRepository(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionError(f"User does not have permission: {permission.value}")

    # --- Financial Year Operations ---
    def create_financial_year(self, user: Users, fy_data: FinancialYearCreate) -> FinancialYear:
        self._check_permission(user, PERMISSIONS.FINANCIAL_YEAR_CREATE)
        return self.financial_year_repo.add_financial_year(fy_data.model_dump())

    def get_financial_year_by_id(self, user: Users, id: int) -> FinancialYear | None:
        self._check_permission(user, PERMISSIONS.FINANCIAL_YEAR_SEARCH)
        return self.financial_year_repo.get_financial_year_by_id(id)

    def update_financial_year(self, user: Users, id: int, fy_data: FinancialYearUpdate) -> FinancialYear | None:
        self._check_permission(user, PERMISSIONS.FINANCIAL_YEAR_UPDATE)
        return self.financial_year_repo.update_financial_year(id, fy_data.model_dump(exclude_unset=True))

    def search_financial_years(self, user: Users, filters: FilterFinancialYearSearch) -> list[FinancialYear]:
        self._check_permission(user, PERMISSIONS.FINANCIAL_YEAR_SEARCH)
        return self.financial_year_repo.get_financial_years_by_filter(filters.model_dump(exclude_unset=True))

    # --- System Logs Operations ---
    def create_log(self, log_data: CreateLogs) -> Logs:
        # Note: Log creation by the system does not require user context/permission checks
        return self.log_repo.create_logs(log_data.model_dump())

    def search_logs(self, user: Users, filters: FilteredLogSearch) -> list[Logs]:
        self._check_permission(user, PERMISSIONS.LOG_VIEW)
        return self.log_repo.get_logs_by_filter(filters.model_dump(exclude_unset=True))
