from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.enums import USER_TYPE
from backend.app.db.base import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    user_type = Column(Enum(USER_TYPE, name="usertype", native_enum = True), nullable=False)
    password = Column(String, nullable=False)
    user_office = Column(Integer, ForeignKey("offices.id", ondelete="RESTRICT"), nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)
    
    office = relationship("Offices", back_populates="user")

    logs = relationship(
        "Logs",
        back_populates="user",
        uselist=True, 
        cascade="all"
    )

    darta = relationship(
        "Darta",
        back_populates="user",
        uselist=True, 
        cascade="all"
    )
    
    chalan = relationship(
        "Chalan",
        back_populates="user",
        uselist=True, 
        cascade="all"
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan",
    )