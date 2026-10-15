from fastapi import Cookie, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.security import decode_access_token
from backend.app.repositories import UsersRepository
from backend.app.db.base import get_db

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    access_token: str | None = Cookie(None),
    db: Session = Depends(get_db)
):
    token = None
    if auth_credentials and auth_credentials.credentials:
        token = auth_credentials.credentials
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing access token"
        )

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or expired token"
        )

    user = UsersRepository(db).get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: User not found"
        )

    if user.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: User is inactive"
        )

    return user
