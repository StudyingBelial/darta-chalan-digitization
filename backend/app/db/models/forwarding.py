from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class DocumentForwarding(Base):
    __tablename__ = "document_forwarding"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    document_type = Column(String, nullable=False) # 'DARTA' or 'CHALAN'
    document_id = Column(Integer, nullable=False)
    
    forwarded_by_user = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    forwarded_to_office = Column(Integer, ForeignKey("offices.id", ondelete="RESTRICT"), nullable=True)
    forwarded_to_department = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True)
    forwarded_to_officer = Column(Integer, ForeignKey("officers.id", ondelete="RESTRICT"), nullable=True)
    
    remarks = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="FORWARDED")
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    sender_user = relationship("Users", foreign_keys=[forwarded_by_user])
    target_office = relationship("Offices", foreign_keys=[forwarded_to_office])
    target_department = relationship("Departments", foreign_keys=[forwarded_to_department])
    target_officer = relationship("Officers", foreign_keys=[forwarded_to_officer])
