from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Departments(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    is_disabled = Column(Boolean, nullable=False, default=False)

    officers = relationship(
        "Officers",
        back_populates="departments",
        uselist=True,
        cascade="all"
    )

    chalan = relationship(
        "Chalan",
        back_populates="department",
        uselist=True,
        cascade="all"
    )

    darta = relationship(
        "Darta",
        back_populates="department",
        uselist=True,
        cascade="all"
    )