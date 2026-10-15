from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Officers(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(String, nullable=False)
    department = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"))
    office = Column(Integer, ForeignKey("offices.id", ondelete="RESTRICT"))
    is_disabled = Column(Boolean, nullable=False, default=False)

    offices = relationship("Offices", back_populates="officer")
    departments = relationship("Departments", back_populates="officers")

    chalan = relationship(
        "Chalan",
        back_populates="officer",
        uselist=True,
        cascade="all"
    )

    darta = relationship(
        "Darta",
        back_populates="officer",
        uselist=True,
        cascade="all"
    )