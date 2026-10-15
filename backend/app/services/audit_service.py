from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.db.models.users import Users
from backend.app.db.models.logs import Logs
from backend.app.enums import LOG_TYPE, LOG_SOURCE
from backend.app.repositories.logs import LogRepository
from backend.app.core.logger import logger

class AuditLogService:
    def __init__(self, db: Session):
        self.db = db
        self.log_repo = LogRepository(db)

    def log_event(
        self,
        message: str,
        log_type: LOG_TYPE = LOG_TYPE.INFO,
        source: LOG_SOURCE = LOG_SOURCE.SYSTEM,
        user_id: int | None = None,
        office_id: int | None = None
    ) -> Logs:
        """
        Record a system or user audit event log into the database.
        """
        log_data = {
            "message": message,
            "log_type": log_type,
            "source": source,
            "timestamp": datetime.now(timezone.utc),
            "user_id": user_id,
            "office_id": office_id
        }
        try:
            db_log = self.log_repo.create_logs(log_data)
            logger.info(f"Audit Log [{log_type.value}] ({source.value}): {message}")
            return db_log
        except Exception as e:
            logger.error(f"Failed to write audit log entry to database: {e}")
            raise e

    def log_user_action(
        self,
        user: Users,
        message: str,
        log_type: LOG_TYPE = LOG_TYPE.INFO
    ) -> Logs:
        """
        Convenience method to log an action performed by a logged-in user.
        """
        user_id = user.id if user else None
        office_id = getattr(user, "user_office", None) if user else None
        return self.log_event(
            message=message,
            log_type=log_type,
            source=LOG_SOURCE.USER,
            user_id=user_id,
            office_id=office_id
        )
