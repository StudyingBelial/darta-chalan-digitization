from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.users import (
    UserCreate,
    UserUpdateSelf,
    UserUpdateOther,
    UserUpdateOtherStatus,
    ChangeSelfPassword,
    ChangeOtherPassword,
    FilterUserSearch,
)
from backend.app.services.authentication import AuthenticationService
from backend.app.repositories.users import UsersRepository
from backend.app.db.models.users import Users
from backend.app.core.exceptions import PermissionDeniedError

class UsersController:
    @staticmethod
    async def create_user(user_data: UserCreate, current_user: Users, db: Session):
        auth_service = AuthenticationService(db)
        try:
            return auth_service.create_user(current_user, user_data)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def get_users(filter_params: FilterUserSearch, current_user: Users, db: Session):
        auth_service = AuthenticationService(db)
        try:
            return auth_service.search_users(current_user, filter_params)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))

    @staticmethod
    async def get_current_user_profile(current_user: Users):
        return current_user

    @staticmethod
    async def update_current_user_profile(update_data: UserUpdateSelf, current_user: Users, db: Session):
        repo = UsersRepository(db)
        updated = repo.update_user(current_user.id, update_data.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated

    @staticmethod
    async def change_password(password_data: ChangeSelfPassword, current_user: Users, db: Session):
        auth_service = AuthenticationService(db)
        try:
            auth_service.change_password(current_user, password_data)
            return {"message": "Password changed successfully"}
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def get_user_by_id(user_id: int, current_user: Users, db: Session):
        repo = UsersRepository(db)
        user = repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        return user

    @staticmethod
    async def update_user(user_id: int, update_data: UserUpdateOther, current_user: Users, db: Session):
        repo = UsersRepository(db)
        updated = repo.update_user(user_id, update_data.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        return updated

    @staticmethod
    async def update_user_status(user_id: int, status_data: UserUpdateOtherStatus, current_user: Users, db: Session):
        auth_service = AuthenticationService(db)
        try:
            return auth_service.change_user_status(current_user, user_id, status_data.is_disabled)
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    async def reset_user_password(user_id: int, password_data: ChangeOtherPassword, current_user: Users, db: Session):
        auth_service = AuthenticationService(db)
        try:
            password_data.user_id = user_id
            auth_service.change_other_password(current_user, password_data)
            return {"message": "User password reset successfully"}
        except PermissionError as e:
            raise PermissionDeniedError(str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
