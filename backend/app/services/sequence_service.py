from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db import Darta, Chalan
from backend.app.core.logger import logger

class SequenceService:
    @staticmethod
    def generate_next_darta_id(db: Session, office_id: int, financial_year_id: int | None = None) -> int:
        """
        Generate the next sequential Darta number for a specific office and financial year.
        Sequence restarts from 1 for each office per financial year.
        """
        query = db.query(func.max(Darta.darta_id)).filter(Darta.receiver_office == office_id)
        if financial_year_id:
            query = query.filter(Darta.financial_year == financial_year_id)
            
        max_id = query.scalar()
        next_id = (max_id or 0) + 1
        logger.info(f"Generated next Darta ID {next_id} for office_id={office_id}, fy_id={financial_year_id}")
        return next_id

    @staticmethod
    def generate_next_chalan_id(db: Session, office_id: int) -> int:
        """
        Generate the next sequential Chalan number for a specific sender office.
        """
        query = db.query(func.max(Chalan.chalan_id)).filter(Chalan.sender_office == office_id)
        max_id = query.scalar()
        next_id = (max_id or 0) + 1
        logger.info(f"Generated next Chalan ID {next_id} for office_id={office_id}")
        return next_id
