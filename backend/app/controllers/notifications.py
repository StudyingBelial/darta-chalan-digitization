from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from backend.app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkRead
)
from backend.app.services.notification_service import NotificationService
from backend.app.db.models.users import Users

class NotificationController:
    @staticmethod
    async def get_notifications(
        unread_only: bool,
        limit: int,
        offset: int,
        current_user: Users,
        db: Session
    ) -> NotificationListResponse:
        notif_service = NotificationService(db)
        items = notif_service.get_user_notifications(
            current_user=current_user,
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )
        unread_count = notif_service.get_unread_count(current_user)
        
        response_items = [NotificationResponse.model_validate(n) for n in items]
        return NotificationListResponse(
            items=response_items,
            unread_count=unread_count,
            total_count=len(response_items)
        )

    @staticmethod
    async def mark_as_read(
        notification_id: int,
        current_user: Users,
        db: Session
    ) -> NotificationResponse:
        notif_service = NotificationService(db)
        notif = notif_service.mark_as_read(notification_id)
        if not notif:
            raise HTTPException(status_code=404, detail=f"Notification #{notification_id} not found.")
        return NotificationResponse.model_validate(notif)

    @staticmethod
    async def mark_all_as_read(
        current_user: Users,
        db: Session
    ) -> dict:
        notif_service = NotificationService(db)
        count = notif_service.mark_all_as_read(current_user)
        return {"message": f"Marked {count} notifications as read", "updated_count": count}
