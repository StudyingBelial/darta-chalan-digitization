from pydantic import BaseModel, model_validator
from typing import Optional, Literal
from datetime import date

class CreateDarta(BaseModel):
    darta_id: int
    sender: str
    sender_email: str
    sender_contact_number: Optional[str] = None
    darta_date: date
    financial_year: int
    topic: str
    file_name: str
    receiver_department: int
    receiver_officer: int
    
    model_config = {"from_attributes":True}

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
    darta_id: int
    sender: str
    sender_email: str
    sender_contact_number: Optional[str] = None
    darta_date: date
    topic: str
    file_name: str
    financial_year: Optional[DartaFinancialYearResponse] = None
    department: Optional[DartaDepartmentResponse] = None
    officer: Optional[DartaOfficerResponse] = None

    model_config = {"from_attributes":True}

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
                "darta_id": getattr(data, "darta_id", None),
                "sender": getattr(data, "sender", None),
                "sender_email": getattr(data, "sender_email", None),
                "sender_contact_number": getattr(data, "sender_contact_number", None),
                "darta_date": getattr(data, "darta_date", None),
                "topic": getattr(data, "topic", None),
                "file_name": getattr(data, "file_name", None),
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
    financial_year: Optional[int] = None
    topic: Optional[str] = None
    receiver_office: Optional[int] = None
    receiver_department: Optional[int] = None
    receiver_officer: Optional[int] = None
    issued_by_user: Optional[int] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"