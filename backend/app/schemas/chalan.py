from pydantic import BaseModel, model_validator
from typing import Optional, Literal
from datetime import date

class CreateChalan(BaseModel):
    chalan_id: int
    sender_email: str
    receiver: str
    receiver_email: str
    receiver_contact_number: Optional[str] = None
    chalan_date: date
    topic: str
    file_name: str
    sender_department: int
    sender_officer: int

class ReceiverResponse(BaseModel):
    name: str
    email: str
    contact_number: Optional[str] = None

class SenderResponse(BaseModel):
    email: str
    department_id: Optional[int] = None
    department: Optional[str] = None
    officer_id: Optional[int] = None
    officer: Optional[str] = None

class ChalanResponse(BaseModel):
    chalan_id: int
    chalan_date: date
    topic: str
    file_name: str
    receiver: ReceiverResponse
    sender: SenderResponse

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def construct_nested_fields(cls, data):
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            receiver_data = {
                "name": getattr(data, "receiver", None),
                "email": getattr(data, "receiver_email", None),
                "contact_number": getattr(data, "receiver_contact_number", None)
            }
            
            dept = getattr(data, "department", None)
            dept_name = dept.name if dept else None
            
            off = getattr(data, "officer", None)
            off_name = off.name if off else None
            
            sender_data = {
                "email": getattr(data, "sender_email", None),
                "department_id": getattr(data, "sender_department", None),
                "department": dept_name,
                "officer_id": getattr(data, "sender_officer", None),
                "officer": off_name
            }
            
            return {
                "chalan_id": getattr(data, "chalan_id", None),
                "chalan_date": getattr(data, "chalan_date", None),
                "topic": getattr(data, "topic", None),
                "file_name": getattr(data, "file_name", None),
                "receiver": receiver_data,
                "sender": sender_data
            }
        return data

class FilterChalanSearch(BaseModel):
    id: Optional[int] = None
    chalan_id: Optional[int] = None
    sender_email: Optional[str] = None
    receiver: Optional[str] = None
    receiver_email: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    topic: Optional[str] = None
    sender_office: Optional[int] = None
    sender_department: Optional[int] = None
    sender_officer: Optional[int] = None
    issued_by_user: Optional[int] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"