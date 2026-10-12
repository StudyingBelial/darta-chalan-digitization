from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Date, func
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Chalan(Base):
    __tablename__ = "chalan"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    chalan_id = Column(Integer, nullable=False)
    issued_by_user = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    sender_email = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    receiver_email = Column(String, nullable=False)
    receiver_contact_number = Column(String, nullable=True)
    chalan_date = Column(Date, nullable=False)
    chalan_date_bs = Column(String, nullable=True)
    topic = Column(String, nullable=True, default="None")
    file_name = Column(String, nullable=False, unique=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    extracted_ocr_text = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="REGISTERED")
    sender_office = Column(Integer, ForeignKey("offices.id", ondelete="RESTRICT"))
    sender_department = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"))
    sender_officer = Column(Integer, ForeignKey("officers.id", ondelete="RESTRICT"))

    user = relationship("Users", back_populates="chalan")
    office = relationship("Offices", back_populates="chalan")
    department = relationship("Departments", back_populates="chalan")
    officer = relationship("Officers", back_populates="chalan")