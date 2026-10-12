import pytest
from backend.app.services.authentication import AuthenticationService
from backend.app.schemas import UserLogin
from backend.app.enums import USER_TYPE

def test_login_success(db_session, test_staff_user):
    auth_service = AuthenticationService(db_session)
    login_data = UserLogin(
        email=test_staff_user.email,
        password="Secret123!",
        user_type=USER_TYPE.STAFF
    )

    result = auth_service.login(login_data)
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["user"].id == test_staff_user.id

def test_login_invalid_password(db_session, test_staff_user):
    auth_service = AuthenticationService(db_session)
    login_data = UserLogin(
        email=test_staff_user.email,
        password="WrongPassword!",
        user_type=USER_TYPE.STAFF
    )

    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_service.login(login_data)

def test_refresh_session(db_session, test_staff_user):
    auth_service = AuthenticationService(db_session)
    login_data = UserLogin(
        email=test_staff_user.email,
        password="Secret123!",
        user_type=USER_TYPE.STAFF
    )

    result = auth_service.login(login_data)
    refresh_token = result["refresh_token"]

    new_tokens = auth_service.refresh_session(refresh_token)
    assert "access_token" in new_tokens
