from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.logger import logger
from backend.app.services.audit_service import AuditLogService
from backend.app.repositories.notification import NotificationRepository
from backend.app.db.models.notification import Notification
from backend.app.db.models.users import Users
from backend.app.enums import LOG_TYPE, LOG_SOURCE

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditLogService(db)
        self.notification_repo = NotificationRepository(db)

    def notify_forwarding(
        self,
        sender_user_name: str,
        document_type: str,
        document_id: int,
        target_office_id: int | None = None,
        target_department_id: int | None = None,
        target_officer_email: str | None = None,
        remarks: str | None = None
    ) -> bool:
        """
        Dispatch notification regarding document forwarding.
        Persists alert in notification table and logs to audit system.
        """
        doc_type = document_type.upper()
        title = f"{doc_type} #{document_id} Forwarded to Your Office"
        msg = (
            f"{doc_type} #{document_id} was forwarded by {sender_user_name}. "
            f"Remarks: {remarks or 'None'}"
        )
        logger.info(msg)

        # Persist notification for staff/admin
        self.notification_repo.create({
            "target_office_id": target_office_id,
            "target_role": "STAFF",
            "title": title,
            "message": msg,
            "notification_type": "DOCUMENT_FORWARDED",
            "darta_id": document_id if doc_type == "DARTA" else None,
            "chalan_id": document_id if doc_type == "CHALAN" else None,
            "action_url": f"/{doc_type.lower()}?highlight={document_id}"
        })

        # Audit log notification event
        self.audit_service.log_event(
            message=msg,
            log_type=LOG_TYPE.INFO,
            source=LOG_SOURCE.SYSTEM,
            office_id=target_office_id
        )

        return True

    def get_user_notifications(
        self,
        current_user: Users,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        return self.notification_repo.list_user_notifications(
            user_id=current_user.id,
            office_id=current_user.user_office,
            role=current_user.user_type.value if hasattr(current_user.user_type, "value") else str(current_user.user_type),
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )

    def get_unread_count(self, current_user: Users) -> int:
        return self.notification_repo.count_unread(
            user_id=current_user.id,
            office_id=current_user.user_office,
            role=current_user.user_type.value if hasattr(current_user.user_type, "value") else str(current_user.user_type)
        )

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        return self.notification_repo.mark_as_read(notification_id)

    def mark_all_as_read(self, current_user: Users) -> int:
        return self.notification_repo.mark_all_as_read(
            user_id=current_user.id,
            office_id=current_user.user_office,
            role=current_user.user_type.value if hasattr(current_user.user_type, "value") else str(current_user.user_type)
        )
