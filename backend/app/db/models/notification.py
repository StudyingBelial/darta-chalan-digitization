from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Null if targeted to role/office
    target_office_id = Column(Integer, ForeignKey("offices.id", ondelete="CASCADE"), nullable=True)
    target_role = Column(String, nullable=True)  # e.g., "STAFF", "OFFICE_ADMIN", "ALL"
    
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, nullable=False, default="INBOUND_EMAIL")  # INBOUND_EMAIL, DOCUMENT_FORWARDED, SCAN_INTAKE, SYSTEM_ALERT
    
    inbound_doc_id = Column(Integer, ForeignKey("inbound_documents.id", ondelete="CASCADE"), nullable=True)
    darta_id = Column(Integer, ForeignKey("darta.id", ondelete="SET NULL"), nullable=True)
    chalan_id = Column(Integer, ForeignKey("chalan.id", ondelete="SET NULL"), nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False)
    action_url = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("Users", foreign_keys=[user_id])
    office = relationship("Offices", foreign_keys=[target_office_id])
    inbound_document = relationship("InboundDocument", back_populates="notifications", foreign_keys=[inbound_doc_id])
