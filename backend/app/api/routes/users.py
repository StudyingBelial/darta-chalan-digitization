from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdateSelf,
    UserUpdateOther,
    UserUpdateOtherStatus,
    ChangeSelfPassword,
    ChangeOtherPassword,
    FilterUserSearch,
)
from backend.app.controllers.users import UsersController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.create_user(user_data, current_user, db)

@router.get("", response_model=List[UserResponse])
async def get_users(
    filter_params: FilterUserSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.get_users(filter_params, current_user, db)

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Users = Depends(get_current_user)
):
    return await UsersController.get_current_user_profile(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdateSelf,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.update_current_user_profile(update_data, current_user, db)

@router.put("/me/password")
async def change_password(
    password_data: ChangeSelfPassword,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.change_password(password_data, current_user, db)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.get_user_by_id(user_id, current_user, db)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdateOther,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.update_user(user_id, update_data, current_user, db)

@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    status_data: UserUpdateOtherStatus,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.update_user_status(user_id, status_data, current_user, db)

@router.put("/{user_id}/password")
async def reset_user_password(
    user_id: int,
    password_data: ChangeOtherPassword,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await UsersController.reset_user_password(user_id, password_data, current_user, db)
