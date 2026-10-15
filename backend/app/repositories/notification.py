from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from backend.app.db.models.notification import Notification

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(Notification.id == id).first()

    def create(self, data: Dict[str, Any]) -> Notification:
        notif = Notification(**data)
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def list_user_notifications(
        self,
        user_id: Optional[int] = None,
        office_id: Optional[int] = None,
        role: Optional[str] = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        query = self.db.query(Notification)

        # Filters: direct user match OR office/role broadcast
        filters = []
        if user_id:
            filters.append(Notification.user_id == user_id)
        if office_id:
            filters.append((Notification.target_office_id == office_id) | (Notification.target_office_id.is_(None)))
        if role:
            filters.append((Notification.target_role == role) | (Notification.target_role == "ALL") | (Notification.target_role.is_(None)))

        if filters:
            from sqlalchemy import or_
            query = query.filter(or_(*filters))

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    def count_unread(
        self,
        user_id: Optional[int] = None,
        office_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> int:
        query = self.db.query(Notification).filter(Notification.is_read == False)
        
        filters = []
        if user_id:
            filters.append(Notification.user_id == user_id)
        if office_id:
            filters.append((Notification.target_office_id == office_id) | (Notification.target_office_id.is_(None)))
        if role:
            filters.append((Notification.target_role == role) | (Notification.target_role == "ALL") | (Notification.target_role.is_(None)))

        if filters:
            from sqlalchemy import or_
            query = query.filter(or_(*filters))

        return query.count()

    def mark_as_read(self, id: int) -> Optional[Notification]:
        notif = self.get_by_id(id)
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def mark_all_as_read(
        self,
        user_id: Optional[int] = None,
        office_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> int:
        query = self.db.query(Notification).filter(Notification.is_read == False)
        filters = []
        if user_id:
            filters.append(Notification.user_id == user_id)
        if office_id:
            filters.append(Notification.target_office_id == office_id)
        if role:
            filters.append(Notification.target_role == role)

        if filters:
            from sqlalchemy import or_
            query = query.filter(or_(*filters))

        count = query.update({"is_read": True}, synchronize_session=False)
        self.db.commit()
        return count
