from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Date, func
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Darta(Base):
    __tablename__ = "darta"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    darta_id = Column(Integer, nullable=False)
    issued_by_user = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    sender = Column(String, nullable=False)
    sender_email = Column(String, nullable=False)
    sender_contact_number = Column(String, nullable=True)
    darta_date = Column(Date, nullable=False)
    darta_date_bs = Column(String, nullable=True)
    financial_year = Column(Integer, ForeignKey("financial_year.id", ondelete="RESTRICT"))
    topic = Column(String, nullable=False)
    file_name = Column(String, nullable=False, unique=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    extracted_ocr_text = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="REGISTERED")
    receiver_office = Column(Integer, ForeignKey("offices.id", ondelete="RESTRICT"))
    receiver_department = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"))
    receiver_officer = Column(Integer, ForeignKey("officers.id", ondelete="RESTRICT"))

    user = relationship("Users", back_populates="darta")
    financ_year = relationship("FinancialYear", back_populates="darta")
    office = relationship("Offices", back_populates="darta")
    department = relationship("Departments", back_populates="darta")
    officer = relationship("Officers", back_populates="darta")