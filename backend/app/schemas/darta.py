from pydantic import BaseModel, model_validator
from typing import Optional, Literal
from datetime import date

from fastapi import Form

class CreateDarta(BaseModel):
    darta_id: Optional[int] = None
    sender: str
    sender_email: str
    sender_contact_number: Optional[str] = None
    darta_date: date
    darta_date_bs: Optional[str] = None
    financial_year: int
    topic: str
    file_name: Optional[str] = None
    receiver_department: Optional[int] = None
    receiver_officer: Optional[int] = None
    extracted_ocr_text: Optional[str] = None
    status: Optional[str] = "REGISTERED"
    
    model_config = {"from_attributes": True}

    @classmethod
    def as_form(
        cls,
        sender: str = Form(...),
        sender_email: str = Form(...),
        darta_date: date = Form(...),
        financial_year: int = Form(...),
        topic: str = Form(...),
        darta_id: Optional[int] = Form(None),
        sender_contact_number: Optional[str] = Form(None),
        darta_date_bs: Optional[str] = Form(None),
        file_name: Optional[str] = Form(None),
        receiver_department: Optional[int] = Form(None),
        receiver_officer: Optional[int] = Form(None),
        extracted_ocr_text: Optional[str] = Form(None),
        status: Optional[str] = Form("REGISTERED"),
    ):
        return cls(
            darta_id=darta_id,
            sender=sender,
            sender_email=sender_email,
            sender_contact_number=sender_contact_number,
            darta_date=darta_date,
            darta_date_bs=darta_date_bs,
            financial_year=financial_year,
            topic=topic,
            file_name=file_name,
            receiver_department=receiver_department,
            receiver_officer=receiver_officer,
            extracted_ocr_text=extracted_ocr_text,
            status=status,
        )

class DartaDepartmentResponse(BaseModel):
    receiver_department_id: Optional[int] = None
    receiver_department: Optional[str] = None

class DartaFinancialYearResponse(BaseModel):
    financial_year_id: Optional[int] = None
    financial_year: Optional[str] = None

class DartaOfficerResponse(BaseModel):
    receiver_officer_id: Optional[int] = None
    receiver_officer: Optional[str] = None

class DartaResponse(BaseModel):
    id: Optional[int] = None
    darta_id: int
    sender: str
    sender_email: str
    sender_contact_number: Optional[str] = None
    darta_date: date
    darta_date_bs: Optional[str] = None
    topic: str
    file_name: str
    extracted_ocr_text: Optional[str] = None
    status: Optional[str] = "REGISTERED"
    financial_year: Optional[DartaFinancialYearResponse] = None
    department: Optional[DartaDepartmentResponse] = None
    officer: Optional[DartaOfficerResponse] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def construct_nested_fields(cls, data):
        if hasattr(data, "__dict__") or not isinstance(data, dict):
            # Extract financial year details
            f_year = getattr(data, "financ_year", None)
            financial_year_data = None
            if f_year:
                financial_year_data = {
                    "financial_year_id": f_year.id,
                    "financial_year": f_year.financial_year
                }
            
            # Extract department details
            dept = getattr(data, "department", None)
            department_data = None
            if dept:
                department_data = {
                    "receiver_department_id": dept.id,
                    "receiver_department": dept.name
                }
                
            # Extract officer details
            off = getattr(data, "officer", None)
            officer_data = None
            if off:
                officer_data = {
                    "receiver_officer_id": off.id,
                    "receiver_officer": off.name
                }
                
            return {
                "id": getattr(data, "id", None),
                "darta_id": getattr(data, "darta_id", None),
                "sender": getattr(data, "sender", None),
                "sender_email": getattr(data, "sender_email", None),
                "sender_contact_number": getattr(data, "sender_contact_number", None),
                "darta_date": getattr(data, "darta_date", None),
                "darta_date_bs": getattr(data, "darta_date_bs", None),
                "topic": getattr(data, "topic", None),
                "file_name": getattr(data, "file_name", None),
                "extracted_ocr_text": getattr(data, "extracted_ocr_text", None),
                "status": getattr(data, "status", "REGISTERED"),
                "financial_year": financial_year_data,
                "department": department_data,
                "officer": officer_data
            }
        return data

class FilterDartaSearch(BaseModel):
    id: Optional[int] = None
    darta_id: Optional[int] = None
    sender: Optional[str] = None
    sender_email: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    from_date_bs: Optional[str] = None
    to_date_bs: Optional[str] = None
    financial_year: Optional[int] = None
    topic: Optional[str] = None
    receiver_office: Optional[int] = None
    receiver_department: Optional[int] = None
    receiver_officer: Optional[int] = None
    issued_by_user: Optional[int] = None
    status: Optional[str] = None
    ocr_keyword: Optional[str] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"