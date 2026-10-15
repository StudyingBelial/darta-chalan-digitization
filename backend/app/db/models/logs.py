from sqlalchemy import Integer, String, Column, ForeignKey, TIMESTAMP, Enum, func
from sqlalchemy import text
from sqlalchemy.orm import relationship
from backend.app.enums import LOG_TYPE, LOG_SOURCE
from backend.app.db.base import Base

class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    office_id = Column(Integer, ForeignKey("offices.id", ondelete="RESTRICT"), nullable=True)
    source = Column(Enum(LOG_SOURCE, name="log_source", native_enum=True), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    log_type = Column(Enum(LOG_TYPE, name="log_type", native_enum = True), nullable=False)
    message = Column(String, nullable=False)

    user = relationship("Users", back_populates="logs")
    office = relationship("Offices", back_populates="logs")