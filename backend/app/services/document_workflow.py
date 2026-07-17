from sqlalchemy.orm import Session
from backend.app.db.models.users import Users
from backend.app.enums import PERMISSIONS
from backend.app.core.permissions import has_permission
from backend.app.schemas import (
    CreateDarta, FilterDartaSearch,
    CreateChalan, FilterChalanSearch
)
from backend.app.repositories import DartaRepository, ChalanRepository
from backend.app.db import Darta, Chalan

class DocumentWorkflowService:
    def __init__(self, db: Session):
        self.darta_repo = DartaRepository(db)
        self.chalan_repo = ChalanRepository(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionError(f"User does not have permission: {permission.value}")

    # --- Darta Operations ---
    def create_darta(self, user: Users, darta_data: CreateDarta, file_path: str, receiver_office: int | None = None) -> Darta:
        self._check_permission(user, PERMISSIONS.DARTA_CREATE)
        data = darta_data.model_dump()
        data["issued_by_user"] = user.id
        data["file_path"] = file_path
        data["receiver_office"] = receiver_office or user.user_office
        return self.darta_repo.create_darta(data)

    def get_darta_by_id(self, user: Users, id: int) -> Darta | None:
        self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        return self.darta_repo.get_darta_by_id(id)

    def update_darta(self, user: Users, id: int, darta_data: dict) -> Darta | None:
        self._check_permission(user, PERMISSIONS.DARTA_UPDATE)
        return self.darta_repo.update_darta(id, darta_data)

    def search_dartas(self, user: Users, filters: FilterDartaSearch) -> list[Darta]:
        self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        return self.darta_repo.get_dartas_by_filter(filters.model_dump(exclude_unset=True))

    # --- Chalan Operations ---
    def create_chalan(self, user: Users, chalan_data: CreateChalan, file_path: str, sender_office: int | None = None) -> Chalan:
        self._check_permission(user, PERMISSIONS.CHALAN_CREATE)
        data = chalan_data.model_dump()
        data["issued_by_user"] = user.id
        data["file_path"] = file_path
        data["sender_office"] = sender_office or user.user_office
        return self.chalan_repo.create_chalan(data)

    def get_chalan_by_id(self, user: Users, id: int) -> Chalan | None:
        self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)
        return self.chalan_repo.get_chalan_by_id(id)

    def update_chalan(self, user: Users, id: int, chalan_data: dict) -> Chalan | None:
        self._check_permission(user, PERMISSIONS.CHALAN_UPDATE)
        return self.chalan_repo.update_chalan(id, chalan_data)

    def search_chalans(self, user: Users, filters: FilterChalanSearch) -> list[Chalan]:
        self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)
        return self.chalan_repo.get_chalans_by_filter(filters.model_dump(exclude_unset=True))
