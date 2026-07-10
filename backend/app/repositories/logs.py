from sqlalchemy.orm import Session

from backend.app.db import Logs

LOG_ORDER_MAP = {
    "id" : Logs.id,
    "user_id" : Logs.user_id,
    "office_id" : Logs.office_id,
    "source" : Logs.source,
    "timestamp" : Logs.timestamp,
    "log_type" : Logs.log_type,
    "message" : Logs.message
}

class LogRepository():
    def __init__(self, db: Session):
        """
        Initialize the logs repository with a database session.
        """
        self.db = db

    def create_logs(self, log_data: dict) -> Logs:
        """
        Create and persist a new system log entry.
        """
        new_log = Logs(**log_data)

        self.db.add(new_log)
        self.db.commit()
        self.db.refresh(new_log)

        return new_log
    
    def get_logs_by_filter(self, filters: dict):
        """
        Retrieve logs matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Logs)

        exact_filters = {
            "id" : Logs.id,
            "user_id" : Logs.user_id,
            "office_id" : Logs.office_id,
            "source" : Logs.source,
            "log_type" : Logs.log_type,
        }

        for key, column in exact_filters.items():
            if (value := filters.get(key)) is not None:
                query = query.filter(column == value)

        if filters.get("start_time") is not None:
            query = query.filter(Logs.timestamp >= filters["start_time"])

        if filters.get("end_time") is not None:
            query = query.filter(Logs.timestamp <= filters["end_time"])

        order_col = LOG_ORDER_MAP.get(filters.get("order_by"), Logs.timestamp)

        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()