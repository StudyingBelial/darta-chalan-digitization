from sqlalchemy.orm import Session

from backend.app.db import Departments

DEPARTMENT_ORDER_MAP = {
    "id" : Departments.id,
    "name" : Departments.name,
    "is_disabled" : Departments.is_disabled
}

class DepartmentsRepository:
    def __init__(self, db: Session):
        """
        Initialize the departments repository with a database session.
        """
        self.db = db

    def get_department_by_id(self, id: int) -> Departments | None:
        """
        Retrieve a department from the database by its primary key ID.
        """
        return self.db.get(Departments, id)

    def get_department_by_name(self, name: str) -> Departments | None:
        """
        Retrieve a department from the database by its unique name.
        """
        return self.db.query(Departments).filter(Departments.name.ilike(f"%{name}%")).first()

    def create_department(self, dept_data: dict) -> Departments:
        """
        Create and persist a new department record.
        """
        new_dept = Departments(**dept_data)

        self.db.add(new_dept)
        self.db.commit()
        self.db.refresh(new_dept)

        return new_dept
    
    def update_department(self, id: int, dept_data: dict) -> Departments | None:
        """
        Update an existing department record.
        """
        dept = self.get_department_by_id(id)
        if not dept:
            return None
        
        for k, v in dept_data.items():
            setattr(dept, k, v)
            
        self.db.commit()
        self.db.refresh(dept)
        return dept
    
    def get_departments_by_filter(self, filters: dict) -> list[Departments]:
        """
        Retrieve departments matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Departments)

        if filters.get("id") is not None:
            query = query.filter(Departments.id == filters["id"])
        if (name := filters.get("name")) is not None:
            query = query.filter(Departments.name.ilike(f"%{name}%"))
        if filters.get("is_disabled") is not None:
            query = query.filter(Departments.is_disabled == filters["is_disabled"])

        order_col = DEPARTMENT_ORDER_MAP.get(filters.get("order_by"), Departments.id)
        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()