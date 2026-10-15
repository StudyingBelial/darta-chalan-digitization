from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class FinancialYear(Base):
    __tablename__ = "financial_year"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    financial_year = Column(String, unique=True, nullable=False)

    darta = relationship(
        "Darta",
        back_populates="financ_year",
        uselist=True,
        cascade="all"
    )