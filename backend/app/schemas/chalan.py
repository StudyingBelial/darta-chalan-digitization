from pydantic import BaseModel, model_validator
from typing import Optional, Literal
from datetime import date

from fastapi import Form

class CreateChalan(BaseModel):
    chalan_id: Optional[int] = None
    sender_email: str
    receiver: str
    receiver_email: str
    receiver_contact_number: Optional[str] = None
    chalan_date: date
    chalan_date_bs: Optional[str] = None
    topic: str
    file_name: Optional[str] = None
    sender_department: Optional[int] = None
    sender_officer: Optional[int] = None
    extracted_ocr_text: Optional[str] = None
    status: Optional[str] = "REGISTERED"

    @classmethod
    def as_form(
        cls,
        sender_email: str = Form(...),
        receiver: str = Form(...),
        receiver_email: str = Form(...),
        chalan_date: date = Form(...),
        topic: str = Form(...),
        chalan_id: Optional[int] = Form(None),
        receiver_contact_number: Optional[str] = Form(None),
        chalan_date_bs: Optional[str] = Form(None),
        file_name: Optional[str] = Form(None),
        sender_department: Optional[int] = Form(None),
        sender_officer: Optional[int] = Form(None),
        extracted_ocr_text: Optional[str] = Form(None),
        status: Optional[str] = Form("REGISTERED"),
    ):
        return cls(
            chalan_id=chalan_id,
            sender_email=sender_email,
            receiver=receiver,
            receiver_email=receiver_email,
            receiver_contact_number=receiver_contact_number,
            chalan_date=chalan_date,
            chalan_date_bs=chalan_date_bs,
            topic=topic,
            file_name=file_name,
            sender_department=sender_department,
            sender_officer=sender_officer,
            extracted_ocr_text=extracted_ocr_text,
            status=status,
        )

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
    id: Optional[int] = None
    chalan_id: int
    chalan_date: date
    chalan_date_bs: Optional[str] = None
    topic: str
    file_name: str
    extracted_ocr_text: Optional[str] = None
    status: Optional[str] = "REGISTERED"
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
                "id": getattr(data, "id", None),
                "chalan_id": getattr(data, "chalan_id", None),
                "chalan_date": getattr(data, "chalan_date", None),
                "chalan_date_bs": getattr(data, "chalan_date_bs", None),
                "topic": getattr(data, "topic", None),
                "file_name": getattr(data, "file_name", None),
                "extracted_ocr_text": getattr(data, "extracted_ocr_text", None),
                "status": getattr(data, "status", "REGISTERED"),
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
    from_date_bs: Optional[str] = None
    to_date_bs: Optional[str] = None
    topic: Optional[str] = None
    sender_office: Optional[int] = None
    sender_department: Optional[int] = None
    sender_officer: Optional[int] = None
    issued_by_user: Optional[int] = None
    status: Optional[str] = None
    ocr_keyword: Optional[str] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"