from pydantic import BaseModel
from typing import Optional, Literal

class OfficeCreate(BaseModel):
    name: str
    location: str

class OfficeUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    is_disabled: Optional[bool] = None

class FilterOfficeSearch(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[str] = None
    is_disabled: Optional[bool] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"

class OfficeResponse(BaseModel):
    id: int
    name: str
    location: str
    is_disabled: bool

    model_config = {"from_attributes": True}
