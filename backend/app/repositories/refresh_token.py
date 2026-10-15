from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db import RefreshToken

class RefreshTokenRepository:
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        """
        self.db = db

    def create_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """
        Create and persist a new refresh token record.
        """
        db_token = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_active_token(self, token: str) -> RefreshToken | None:
        """
        Retrieve a non-revoked refresh token record by token string.
        """
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False
        ).first()

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a refresh token by updating its is_revoked status to True.
        """
        db_token = self.db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if not db_token:
            return False
        db_token.is_revoked = True
        self.db.commit()
        return True
