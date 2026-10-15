from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse
)
from backend.app.controllers.notifications import NotificationController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications for the logged in staff member or office with unread count.
    """
    return await NotificationController.get_notifications(
        unread_only=unread_only,
        limit=limit,
        offset=offset,
        current_user=current_user,
        db=db
    )

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a single notification as read.
    """
    return await NotificationController.mark_as_read(notification_id, current_user, db)

@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all unread notifications for current user/office as read.
    """
    return await NotificationController.mark_all_as_read(current_user, db)
