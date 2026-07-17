from sqlalchemy.orm import Session
from backend.app.db.models.users import Users
from backend.app.enums import PERMISSIONS
from backend.app.core.permissions import has_permission

from backend.app.schemas import (
    OfficeCreate, OfficeUpdate, FilterOfficeSearch,
    DepartmentCreate, DepartmentUpdate, FilterDepartmentSearch,
    OfficerCreate, OfficerUpdate, FilterOfficerSearch
)

from backend.app.repositories import OfficersRepository, OfficesRepository, DepartmentsRepository

class OrganizationService:
    def __init__(self, db: Session):
        self.office_repo = OfficesRepository(db)
        self.department_repo = DepartmentsRepository(db)
        self.officer_repo = OfficersRepository(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionError(f"User does not have permission: {permission.value}")

    # --- Offices ---
    def create_office(self, user: Users, office_data: OfficeCreate):
        self._check_permission(user, PERMISSIONS.OFFICE_CREATE)
        return self.office_repo.create_office(office_data.model_dump())

    def get_office_by_id(self, user: Users, id: int):
        self._check_permission(user, PERMISSIONS.OFFICE_SEARCH)
        return self.office_repo.get_office_by_id(id)

    def update_office(self, user: Users, id: int, office_data: OfficeUpdate):
        self._check_permission(user, PERMISSIONS.OFFICE_UPDATE)
        return self.office_repo.update_office(id, office_data.model_dump(exclude_unset=True))

    def search_offices(self, user: Users, filters: FilterOfficeSearch):
        self._check_permission(user, PERMISSIONS.OFFICE_SEARCH)
        return self.office_repo.get_offices_by_filter(filters.model_dump(exclude_unset=True))

    # --- Departments ---
    def create_department(self, user: Users, dept_data: DepartmentCreate):
        self._check_permission(user, PERMISSIONS.DEPARTMENT_CREATE)
        return self.department_repo.create_department(dept_data.model_dump())

    def get_department_by_id(self, user: Users, id: int):
        self._check_permission(user, PERMISSIONS.DEPARTMENT_SEARCH)
        return self.department_repo.get_department_by_id(id)

    def update_department(self, user: Users, id: int, dept_data: DepartmentUpdate):
        self._check_permission(user, PERMISSIONS.DEPARTMENT_UPDATE)
        return self.department_repo.update_department(id, dept_data.model_dump(exclude_unset=True))

    def search_departments(self, user: Users, filters: FilterDepartmentSearch):
        self._check_permission(user, PERMISSIONS.DEPARTMENT_SEARCH)
        return self.department_repo.get_departments_by_filter(filters.model_dump(exclude_unset=True))

    # --- Officers ---
    def create_officer(self, user: Users, officer_data: OfficerCreate):
        self._check_permission(user, PERMISSIONS.OFFICER_CREATE)
        return self.officer_repo.create_officer(officer_data.model_dump())

    def get_officer_by_id(self, user: Users, id: int):
        self._check_permission(user, PERMISSIONS.OFFICER_SEARCH)
        return self.officer_repo.get_officer_by_id(id)

    def update_officer(self, user: Users, id: int, officer_data: OfficerUpdate):
        self._check_permission(user, PERMISSIONS.OFFICER_UPDATE)
        return self.officer_repo.update_officer(id, officer_data.model_dump(exclude_unset=True))

    def search_officers(self, user: Users, filters: FilterOfficerSearch):
        self._check_permission(user, PERMISSIONS.OFFICER_SEARCH)
        return self.officer_repo.get_officers_by_filter(filters.model_dump(exclude_unset=True))