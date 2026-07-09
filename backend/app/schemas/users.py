from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from backend.app.enums import USER_TYPE

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    user_type: USER_TYPE
    user_office: int
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    user_type: USER_TYPE
    password: str

class UserUpdateSelf(BaseModel):
    full_name: Optional[str] = None
    email : Optional[EmailStr] = None

class ChangeSelfPassword(BaseModel):
    old_password: str
    new_password : str

class ChangeOtherPassword(BaseModel):
    user_id: int
    new_password: str

class UserUpdateOther(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[USER_TYPE] = None
    user_office: Optional[int] = None
    is_disabled: Optional[int] = None

class UserUpdateOtherStatus(BaseModel):
    user_id: int
    user_status: bool

class FilterUserSearch(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    user_type: Optional[str] = None
    user_office: Optional[str] = None
    user_status: Optional[bool] = None
    order_by: Optional[str] = "id"
    order_direction: Literal["asc", "desc"] = "desc"

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    user_type: USER_TYPE
    is_disabled: bool

    model_config = {"from_attributes": True}