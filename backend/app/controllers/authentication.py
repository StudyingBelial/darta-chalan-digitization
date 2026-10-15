from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.users import UserLogin
from backend.app.schemas.auth import RefreshTokenRequest
from backend.app.services.authentication import AuthenticationService
from backend.app.db.models.users import Users

class AuthenticationController:
    @staticmethod
    async def login(credentials: UserLogin, db: Session):
        auth_service = AuthenticationService(db)
        try:
            result = auth_service.login(credentials)
            return {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "token_type": "bearer",
                "user": result["user"]
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

    @staticmethod
    async def refresh_token(token_data: RefreshTokenRequest, db: Session):
        auth_service = AuthenticationService(db)
        try:
            result = auth_service.refresh_session(token_data.refresh_token)
            return {
                "access_token": result["access_token"],
                "refresh_token": token_data.refresh_token,
                "token_type": "bearer"
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

    @staticmethod
    async def logout(current_user: Users, token_data: RefreshTokenRequest | None, db: Session):
        if token_data and token_data.refresh_token:
            auth_service = AuthenticationService(db)
            auth_service.logout(token_data.refresh_token)
        return {"message": "Logged out successfully"}
