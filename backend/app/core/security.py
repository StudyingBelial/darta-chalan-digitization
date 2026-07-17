from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import secrets
from sqlalchemy.orm import Session
from backend.app.repositories import RefreshTokenRepository

SECRET_KEY = "MY_SUPER_DUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15 # Add an inactivity timer in the background that makes the users inactive
REFRESH_TOKEN_EXPIRE_HOURS = 12

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generate a JWT access token contaiing the payload
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """
    Decode and validate a JWT access token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def create_refresh_token(db: Session, user_id: int, expires_delta: timedelta | None = None) -> str:
    """
    Generate a secure random refresh token, save it to the DB, and return it.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)

    token = secrets.token_urlsafe(32)
    repo = RefreshTokenRepository(db)
    repo.create_refresh_token(user_id=user_id, token=token, expires_at=expire)
    return token

def verify_refresh_token(db: Session, token: str) -> int | None:
    """
    Verify a refresh token against the database.
    Return user_id if valid, None otherwise.
    """
    repo = RefreshTokenRepository(db)
    db_token = repo.get_active_token(token)
    
    if not db_token:
        return None
        
    if db_token.expires_at.tzinfo is None:
        expires_at = db_token.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = db_token.expires_at
        
    if expires_at < datetime.now(timezone.utc):
        return None
        
    return db_token.user_id

def revoke_refresh_token(db: Session, token: str) -> bool:
    """
    Revoke a refresh token in the database.
    """
    repo = RefreshTokenRepository(db)
    return repo.revoke_token(token)