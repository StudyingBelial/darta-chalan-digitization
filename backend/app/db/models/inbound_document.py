from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, JSON, Float, func
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class InboundDocument(Base):
    __tablename__ = "inbound_documents"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    source = Column(String, nullable=False, default="SMTP_EMAIL")  # SMTP_EMAIL, CANON_SCANNER, DIRECT_UPLOAD, API_INTAKE
    sender_email = Column(String, nullable=True)
    sender_name = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    extracted_ocr_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True, default=0.0)
    parsing_status = Column(String, nullable=False, default="PENDING")  # PENDING, PASSED_THRESHOLD, REQUIRES_HUMAN_REVIEW, FAILED
    status = Column(String, nullable=False, default="PENDING_REVIEW")  # PENDING_REVIEW, PARSED, CONVERTED_TO_DARTA, CONVERTED_TO_CHALAN, DISMISSED
    
    target_office_id = Column(Integer, ForeignKey("offices.id", ondelete="SET NULL"), nullable=True)
    target_department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    converted_darta_id = Column(Integer, ForeignKey("darta.id", ondelete="SET NULL"), nullable=True)
    converted_chalan_id = Column(Integer, ForeignKey("chalan.id", ondelete="SET NULL"), nullable=True)
    
    received_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    office = relationship("Offices", foreign_keys=[target_office_id])
    department = relationship("Departments", foreign_keys=[target_department_id])
    assigned_user = relationship("Users", foreign_keys=[assigned_to_user_id])
    converted_darta = relationship("Darta", foreign_keys=[converted_darta_id])
    converted_chalan = relationship("Chalan", foreign_keys=[converted_chalan_id])
    notifications = relationship("Notification", back_populates="inbound_document", cascade="all, delete-orphan")
