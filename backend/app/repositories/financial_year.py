from sqlalchemy.orm import Session

from backend.app.db import FinancialYear

FINANCIAL_YEAR_ORDER_MAP = {
    "id" : FinancialYear.id,
    "year" : FinancialYear.financial_year
}

class FinancialYearRepository:
    def __init__(self, db: Session):
        """
        Initialize the financial year repository with a database session.
        """
        self.db = db

    def get_financial_year_by_id(self, id: int) -> FinancialYear | None:
        """
        Retrieve a financial year from the database by its primary key ID.
        """
        return self.db.get(FinancialYear, id)
    
    def get_financial_year_by_name(self, financial_year: str) -> FinancialYear | None:
        """
        Retrieve a financial year from the database by its year string.
        """
        return self.db.query(FinancialYear).filter(FinancialYear.financial_year.ilike(f"%{financial_year}%")).first()

    def add_financial_year(self, fy_data: dict) -> FinancialYear:
        """
        Create and persist a new financial year record.
        """
        new_fy = FinancialYear(**fy_data)

        self.db.add(new_fy)
        self.db.commit()
        self.db.refresh(new_fy)

        return new_fy
    
    def update_financial_year(self, id: int, fy_data: dict) -> FinancialYear | None:
        """
        Update an existing financial year record.
        """
        fy = self.get_financial_year_by_id(id)
        if not fy:
            return None
        
        for k, v in fy_data.items():
            setattr(fy, k, v)
            
        self.db.commit()
        self.db.refresh(fy)
        return fy
    
    def get_financial_years_by_filter(self, filters: dict) -> list[FinancialYear]:
        """
        Retrieve financial years matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(FinancialYear)

        if filters.get("id") is not None:
            query = query.filter(FinancialYear.id == filters["id"])
        if (year := filters.get("financial_year")) is not None:
            query = query.filter(FinancialYear.financial_year.ilike(f"%{year}%"))

        order_col = FINANCIAL_YEAR_ORDER_MAP.get(filters.get("order_by"), FinancialYear.id)
        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()