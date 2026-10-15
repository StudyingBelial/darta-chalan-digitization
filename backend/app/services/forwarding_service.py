from sqlalchemy.orm import Session
from backend.app.db.models.users import Users
from backend.app.db.models.forwarding import DocumentForwarding
from backend.app.enums import PERMISSIONS, DOCUMENT_STATUS
from backend.app.core.permissions import has_permission
from backend.app.repositories import DartaRepository, ChalanRepository
from backend.app.repositories.forwarding import ForwardingRepository
from backend.app.services.audit_service import AuditLogService
from backend.app.core.exceptions import DocumentNotFoundError, PermissionDeniedError
from backend.app.core.logger import logger

class ForwardingService:
    def __init__(self, db: Session):
        self.db = db
        self.forwarding_repo = ForwardingRepository(db)
        self.darta_repo = DartaRepository(db)
        self.chalan_repo = ChalanRepository(db)
        self.audit_service = AuditLogService(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionDeniedError(f"User does not have permission: {permission.value}")

    def forward_document(
        self,
        user: Users,
        document_type: str,
        document_id: int,
        target_office: int | None = None,
        target_department: int | None = None,
        target_officer: int | None = None,
        remarks: str | None = None
    ) -> DocumentForwarding:
        doc_type_upper = document_type.upper()
        if doc_type_upper == "DARTA":
            self._check_permission(user, PERMISSIONS.DARTA_FORWARD)
            doc = self.darta_repo.get_darta_by_id(document_id)
            if not doc:
                raise DocumentNotFoundError(document_id, "Darta")
            self.darta_repo.update_darta(document_id, {"status": DOCUMENT_STATUS.FORWARDED.value})
        elif doc_type_upper == "CHALAN":
            self._check_permission(user, PERMISSIONS.CHALAN_FORWARD)
            doc = self.chalan_repo.get_chalan_by_id(document_id)
            if not doc:
                raise DocumentNotFoundError(document_id, "Chalan")
            self.chalan_repo.update_chalan(document_id, {"status": DOCUMENT_STATUS.FORWARDED.value})
        else:
            raise ValueError(f"Invalid document type '{document_type}'. Must be 'DARTA' or 'CHALAN'.")

        forwarding_data = {
            "document_type": doc_type_upper,
            "document_id": document_id,
            "forwarded_by_user": user.id,
            "forwarded_to_office": target_office,
            "forwarded_to_department": target_department,
            "forwarded_to_officer": target_officer,
            "remarks": remarks,
            "status": DOCUMENT_STATUS.FORWARDED.value
        }

        record = self.forwarding_repo.create_forwarding(forwarding_data)
        logger.info(f"User {user.id} forwarded {doc_type_upper} #{document_id} to office={target_office}, dept={target_department}, officer={target_officer}")
        self.audit_service.log_user_action(
            user=user,
            message=f"Forwarded {doc_type_upper} #{document_id} to office={target_office}, department={target_department}, officer={target_officer}"
        )
        return record

    def get_forwarding_history(self, user: Users, document_type: str, document_id: int) -> list[DocumentForwarding]:
        doc_type_upper = document_type.upper()
        if doc_type_upper == "DARTA":
            self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        else:
            self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)

        return self.forwarding_repo.get_by_document(doc_type_upper, document_id)
