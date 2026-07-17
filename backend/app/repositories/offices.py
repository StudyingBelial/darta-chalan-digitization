from backend.app.db.models import officers
from sqlalchemy.orm import Session

from backend.app.db import Offices

OFFICES_ORDER_MAP = {
    "id" : Offices.id,
    "name" : Offices.name, 
    "location" : Offices.location,
    "is_disabled" : Offices.is_disabled
}

class OfficesRepository():
    def __init__(self, db: Session):
        """
        Initialize the offices repository with a database session.
        """
        self.db = db

    def get_office_by_id(self, id: int) -> Offices | None:
        """
        Retrieve an office from the database by its primary key ID.
        """
        return self.db.get(Offices, id)

    def get_office_by_name(self, name: str) -> Offices | None:
        """
        Retrieve an office from the database by its name.
        """
        return self.db.query(Offices).filter(Offices.name == name).first()

    def create_office(self, office_data: dict) -> Offices:
        """
        Create and persist a new office record.
        """
        office = Offices(**office_data)
        self.db.add(office)
        self.db.commit()
        self.db.refresh(office)
        return office
    
    def update_office(self, id: int, office_data: dict) -> Offices | None:
        """
        Update an existing office record.
        """
        office = self.get_office_by_id(id)
        if not office:
            return None
        
        for k, v in office_data.items():
            setattr(office, k, v)
            
        self.db.commit()
        self.db.refresh(office)
        return office
    
    def get_offices_by_filter(self, filters: dict) -> list[Offices]:
        """
        Retrieve offices matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Offices)

        if filters.get("id") is not None:
            query = query.filter(Offices.id == filters["id"])

        if (name := filters.get("name")) is not None:
            query = query.filter(Offices.name.ilike(f"%{name}%"))

        if (location := filters.get("location")) is not None:
            query = query.filter(Offices.location.ilike(f"%{location}%"))

        if filters.get("is_disabled") is not None:
            query = query.filter(Offices.is_disabled == filters["is_disabled"])

        order_col = OFFICES_ORDER_MAP.get(filters.get("order_by"), Offices.id)
        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()