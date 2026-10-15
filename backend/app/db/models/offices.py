from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Offices(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    is_disabled = Column(Boolean, nullable=False, default=False)

    user = relationship(
        "Users",
        back_populates="office",
        uselist=True,
        cascade="all"
    )

    officer = relationship(
        "Officers",
        back_populates="offices",
        uselist=True,
        cascade="all"
    )

    chalan = relationship(
        "Chalan",
        back_populates="office",
        uselist=True,
        cascade="all"
    )

    darta = relationship(
        "Darta",
        back_populates="office",
        uselist=True,
        cascade="all"
    )

    logs = relationship(
        "Logs",
        back_populates="office",
        uselist=True,
        cascade="all"
    )