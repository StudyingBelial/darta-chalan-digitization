from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from backend.app.enums import LOG_TYPE, LOG_SOURCE

class CreateLogs(BaseModel):
    user_id: Optional[int] = None
    office_id: Optional[int] = None
    source: LOG_SOURCE
    timestamp: datetime
    log_type: LOG_TYPE
    message: str

class FilteredLogSearch(BaseModel):
    user_id: Optional[int] = None
    office_id: Optional[int] = None
    source: Optional[LOG_SOURCE] = None
    log_type: Optional[LOG_TYPE] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    order_by: Optional[str] = "timestamp"
    order_direction: Literal["asc", "desc"] = "desc"

class LogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    office_id: Optional[int] = None
    source: LOG_SOURCE
    log_type: LOG_TYPE
    timestamp: datetime
    message: str

    model_config = {"from_attributes":True}