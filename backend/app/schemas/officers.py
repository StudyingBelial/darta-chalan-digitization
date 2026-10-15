from pydantic import BaseModel
from typing import Optional, Literal

class OfficerCreate(BaseModel):
    name: str
    department: int
    office: int

class OfficerUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[int] = None
    office: Optional[int] = None
    is_disabled: Optional[bool] = None

class FilterOfficerSearch(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    department: Optional[int] = None
    office: Optional[int] = None
    is_disabled: Optional[bool] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"

class OfficerResponse(BaseModel):
    id: int
    name: str
    department: Optional[int] = None
    office: Optional[int] = None
    is_disabled: bool

    model_config = {"from_attributes": True}
