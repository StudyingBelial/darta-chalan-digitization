from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ForwardingCreate(BaseModel):
    document_type: str # 'DARTA' or 'CHALAN'
    document_id: int
    forwarded_to_office: int | None = None
    forwarded_to_department: int | None = None
    forwarded_to_officer: int | None = None
    remarks: str | None = None

class ForwardingResponse(BaseModel):
    id: int
    document_type: str
    document_id: int
    forwarded_by_user: int
    forwarded_to_office: int | None = None
    forwarded_to_department: int | None = None
    forwarded_to_officer: int | None = None
    remarks: str | None = None
    status: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
