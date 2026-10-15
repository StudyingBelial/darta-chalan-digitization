from pydantic import BaseModel
from typing import Optional
from backend.app.enums import USER_TYPE

from backend.app.schemas.users import UserResponse

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    user_type: Optional[USER_TYPE] = None
