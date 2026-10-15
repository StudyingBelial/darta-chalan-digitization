from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.users import UserLogin
from backend.app.schemas.auth import TokenResponse, RefreshTokenRequest
from backend.app.controllers.authentication import AuthenticationController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return await AuthenticationController.login(credentials, db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return await AuthenticationController.refresh_token(token_data, db)

@router.post("/logout")
async def logout(
    token_data: RefreshTokenRequest | None = None,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await AuthenticationController.logout(current_user, token_data, db)
