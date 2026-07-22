from sqlalchemy.orm import Session
from backend.app.db import Users
from backend.app.enums import PERMISSIONS
from backend.app.core.permissions import has_permission
from backend.app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token
)
from backend.app.schemas import (
    UserLogin,
    ChangeSelfPassword,
    ChangeOtherPassword,
    UserCreate,
    FilterUserSearch
)
from backend.app.repositories import UsersRepository

class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UsersRepository(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionError(f"User does not have permission: {permission.value}")

    def authenticate_user(self, login_data: UserLogin) -> Users:
        """
        Authenticate user credentials.
        Returns the authenticated user on success, or raises ValueError on failure.
        """
        user = self.user_repo.get_user_by_email(login_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        if not verify_password(login_data.password, user.password):
            raise ValueError("Invalid email or password")
            
        if user.user_type != login_data.user_type:
            raise ValueError("Role mismatch")
            
        if user.is_disabled:
            raise ValueError("User account is disabled")
            
        return user

    def login(self, login_data: UserLogin) -> dict:
        """
        Authenticate user and return access and refresh tokens.
        """
        user = self.authenticate_user(login_data)
        
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(db=self.db, user_id=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }

    def refresh_session(self, refresh_token: str) -> dict:
        """
        Refresh access token using a valid, active refresh token.
        """
        user_id = verify_refresh_token(self.db, refresh_token)
        if not user_id:
            raise ValueError("Invalid or expired refresh token")
            
        user = self.user_repo.get_user_by_id(user_id)
        if not user or user.is_disabled:
            raise ValueError("User not found or disabled")
            
        access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token
        }

    def logout(self, refresh_token: str) -> bool:
        """
        Revoke refresh token to logout user.
        """
        return revoke_refresh_token(self.db, refresh_token)

    def change_password(self, user: Users, password_data: ChangeSelfPassword) -> Users:
        """
        Allow a user to change their own password, after verifying the old password.
        """
        self._check_permission(user, PERMISSIONS.USER_SELF_UPDATE)
        
        # Verify old password
        if not verify_password(password_data.old_password, user.password):
            raise ValueError("Incorrect current password")
            
        # Hash new password and update
        hashed_password = hash_password(password_data.new_password)
        updated_user = self.user_repo.change_password(user.id, hashed_password)
        if not updated_user:
            raise ValueError("User not found")
        return updated_user

    def change_other_password(self, admin_user: Users, password_data: ChangeOtherPassword) -> Users:
        """
        Allow an admin to change another user's password.
        """
        self._check_permission(admin_user, PERMISSIONS.USER_OTHER_UPDATE)
        
        hashed_password = hash_password(password_data.new_password)
        updated_user = self.user_repo.change_password(password_data.user_id, hashed_password)
        if not updated_user:
            raise ValueError("Target user not found")
        return updated_user

    def create_user(self, admin_user: Users, user_data: UserCreate) -> Users:
        """
        Allow an admin to create a new user. The password is automatically hashed.
        """
        self._check_permission(admin_user, PERMISSIONS.USER_CREATE)
        
        # Check if email is already taken
        if self.user_repo.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
            
        data = user_data.model_dump()
        data["password"] = hash_password(user_data.password)
        
        return self.user_repo.create_user(data)

    def change_user_status(self, admin_user: Users, user_id: int, user_status: bool) -> Users:
        """
        Allow an admin to enable or disable a user.
        """
        self._check_permission(admin_user, PERMISSIONS.USER_DISABLE)
        updated_user = self.user_repo.change_user_status(user_id, user_status)
        if not updated_user:
            raise ValueError("User not found")
        return updated_user

    def search_users(self, admin_user: Users, filters: FilterUserSearch) -> list[Users]:
        """
        Allow an admin to search users using filters.
        """
        self._check_permission(admin_user, PERMISSIONS.USER_SEARCH)
        return self.user_repo.get_users_by_filter(filters.model_dump(exclude_unset=True))
