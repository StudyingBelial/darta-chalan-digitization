import os
from sqlalchemy.orm import Session
from backend.app.db.models.users import Users
from backend.app.enums import PERMISSIONS, DOCUMENT_STATUS
from backend.app.core.permissions import has_permission
from backend.app.schemas import (
    CreateDarta, FilterDartaSearch,
    CreateChalan, FilterChalanSearch
)
from backend.app.repositories import DartaRepository, ChalanRepository
from backend.app.db import Darta, Chalan
from backend.app.services.date_service import DateService
from backend.app.services.sequence_service import SequenceService
from backend.app.services.ocr_service import OCRService
from backend.app.services.audit_service import AuditLogService
from backend.app.core.exceptions import PermissionDeniedError

class DocumentWorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.darta_repo = DartaRepository(db)
        self.chalan_repo = ChalanRepository(db)
        self.audit_service = AuditLogService(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionDeniedError(f"User does not have permission: {permission.value}")

    # --- Darta Operations ---
    def create_darta(self, user: Users, darta_data: CreateDarta, file_path: str, receiver_office: int | None = None) -> Darta:
        self._check_permission(user, PERMISSIONS.DARTA_CREATE)
        data = darta_data.model_dump()
        
        target_office = receiver_office or user.user_office
        data["issued_by_user"] = user.id
        data["file_path"] = file_path
        data["receiver_office"] = target_office
        if not data.get("file_name") and file_path:
            data["file_name"] = os.path.basename(file_path)
        
        # Auto-generate sequential darta_id if missing or zero
        if not data.get("darta_id"):
            data["darta_id"] = SequenceService.generate_next_darta_id(
                self.db, target_office, data.get("financial_year")
            )

        # Auto B.S. date calculation
        if not data.get("darta_date_bs") and data.get("darta_date"):
            data["darta_date_bs"] = DateService.ad_to_bs(data["darta_date"])

        # Auto OCR text extraction
        if not data.get("extracted_ocr_text") and file_path:
            data["extracted_ocr_text"] = OCRService.extract_text(file_path)

        data["status"] = data.get("status") or DOCUMENT_STATUS.REGISTERED.value

        darta = self.darta_repo.create_darta(data)
        self.audit_service.log_user_action(
            user=user,
            message=f"Created Darta entry #{darta.id} (Darta ID: {darta.darta_id}, Topic: '{darta.topic}')"
        )
        return darta

    def get_darta_by_id(self, user: Users, id: int) -> Darta | None:
        self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        return self.darta_repo.get_darta_by_id(id)

    def update_darta(self, user: Users, id: int, darta_data: dict) -> Darta | None:
        self._check_permission(user, PERMISSIONS.DARTA_UPDATE)
        updated = self.darta_repo.update_darta(id, darta_data)
        if updated:
            self.audit_service.log_user_action(
                user=user,
                message=f"Updated Darta entry #{id}"
            )
        return updated

    def search_dartas(self, user: Users, filters: FilterDartaSearch) -> list[Darta]:
        self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        return self.darta_repo.get_dartas_by_filter(filters.model_dump(exclude_unset=True))

    # --- Chalan Operations ---
    def create_chalan(self, user: Users, chalan_data: CreateChalan, file_path: str, sender_office: int | None = None) -> Chalan:
        self._check_permission(user, PERMISSIONS.CHALAN_CREATE)
        data = chalan_data.model_dump()
        
        target_office = sender_office or user.user_office
        data["issued_by_user"] = user.id
        data["file_path"] = file_path
        data["sender_office"] = target_office
        if not data.get("file_name") and file_path:
            data["file_name"] = os.path.basename(file_path)
        
        # Auto-generate sequential chalan_id if missing or zero
        if not data.get("chalan_id"):
            data["chalan_id"] = SequenceService.generate_next_chalan_id(
                self.db, target_office
            )

        # Auto B.S. date calculation
        if not data.get("chalan_date_bs") and data.get("chalan_date"):
            data["chalan_date_bs"] = DateService.ad_to_bs(data["chalan_date"])

        # Auto OCR text extraction
        if not data.get("extracted_ocr_text") and file_path:
            data["extracted_ocr_text"] = OCRService.extract_text(file_path)

        data["status"] = data.get("status") or DOCUMENT_STATUS.REGISTERED.value

        chalan = self.chalan_repo.create_chalan(data)
        self.audit_service.log_user_action(
            user=user,
            message=f"Created Chalan entry #{chalan.id} (Chalan ID: {chalan.chalan_id}, Receiver: '{chalan.receiver}')"
        )
        return chalan

    def get_chalan_by_id(self, user: Users, id: int) -> Chalan | None:
        self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)
        return self.chalan_repo.get_chalan_by_id(id)

    def update_chalan(self, user: Users, id: int, chalan_data: dict) -> Chalan | None:
        self._check_permission(user, PERMISSIONS.CHALAN_UPDATE)
        updated = self.chalan_repo.update_chalan(id, chalan_data)
        if updated:
            self.audit_service.log_user_action(
                user=user,
                message=f"Updated Chalan entry #{id}"
            )
        return updated

    def search_chalans(self, user: Users, filters: FilterChalanSearch) -> list[Chalan]:
        self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)
        return self.chalan_repo.get_chalans_by_filter(filters.model_dump(exclude_unset=True))
