from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    target_office_id: Optional[int] = None
    target_role: Optional[str] = None
    title: str
    message: str
    notification_type: str
    inbound_doc_id: Optional[int] = None
    darta_id: Optional[int] = None
    chalan_id: Optional[int] = None
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    unread_count: int
    total_count: int

class NotificationMarkRead(BaseModel):
    notification_ids: Optional[List[int]] = None
    mark_all: bool = False
