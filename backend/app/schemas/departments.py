from pydantic import BaseModel
from typing import Optional, Literal

class DepartmentCreate(BaseModel):
    name: str

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    is_disabled: Optional[bool] = None

class FilterDepartmentSearch(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    is_disabled: Optional[bool] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"

class DepartmentResponse(BaseModel):
    id: int
    name: str
    is_disabled: bool

    model_config = {"from_attributes": True}
