from sqlalchemy.orm import Session

from backend.app.db import Officers

OFFICER_ORDER_MAP = {
    "id" : Officers.id,
    "name" : Officers.name,
    "department" : Officers.department,
    "office" : Officers.office,
    "is_disabled" : Officers.is_disabled
}

class OfficersRepository:
    def __init__(self, db: Session):
        """
        Initialize the officers repository with a database session.
        """
        self.db = db

    def get_officer_by_id(self, id: int) -> Officers | None:
        """
        Retrieve an officer from the database by their primary key ID.
        """
        return self.db.get(Officers, id)
    
    def create_officer(self, officer_data: dict) -> Officers:
        """
        Create and persist a new officer record.
        """
        new_officer = Officers(**officer_data)

        self.db.add(new_officer)
        self.db.commit()
        self.db.refresh(new_officer)

        return new_officer
    
    def update_officer(self, id: int, officer_data: dict) -> Officers | None:
        """
        Update an existing officer record.
        """
        officer = self.get_officer_by_id(id)
        if not officer:
            return None
        
        for k, v in officer_data.items():
            setattr(officer, k, v)
            
        self.db.commit()
        self.db.refresh(officer)
        return officer
    
    def get_officers_by_filter(self, filters: dict) -> list[Officers]:
        """
        Retrieve officers matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Officers)

        if filters.get("id") is not None:
            query = query.filter(Officers.id == filters["id"])

        if (name := filters.get("name")) is not None:
            query = query.filter(Officers.name.ilike(f"%{name}%"))
        if (department := filters.get("department")) is not None:
            query = query.filter(Officers.department.ilike(f"%{department}%"))
        if (office := filters.get("office")) is not None:
            query = query.filter(Officers.office.ilike(f"%{office}%"))

        if filters.get("is_disabled") is not None:
            query = query.filter(Officers.is_disabled == filters["is_disabled"])

        order_col = OFFICER_ORDER_MAP.get(filters.get("order_by"), Officers.id)
        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()