from sqlalchemy.orm import Session

from backend.app.db import Darta

DARTA_ORDER_MAP = {
    "id" : Darta.id,
    "darta_id" : Darta.darta_id,
    "issused_by_user" : Darta.issued_by_user,
    "sender" : Darta.sender,
    "sender_email" : Darta.sender_email,
    "sender_contact_number" : Darta.sender_contact_number,
    "darta_date" : Darta.darta_date,
    "financial_year" : Darta.financial_year,
    "topic" : Darta.topic,
    "receiver_office" : Darta.receiver_office,
    "receiver_officer" : Darta.receiver_officer,
    "receiver_department" : Darta.receiver_department
}

class DartaRepository:
    def __init__(self, db: Session):
        """
        Initialize the darta repository with a database session.
        """
        self.db = db

    def get_darta_by_id(self, id: int) -> Darta | None:
        """
        Retrieve a darta from the database by its primary key ID.
        """
        return self.db.get(Darta, id)

    def get_darta_by_darta_id(self, darta_id: int) -> list[Darta]:
        """
        Retrieve dartas matching the register/reference darta_id.
        """
        return self.db.query(Darta).filter(Darta.darta_id == darta_id).all()

    def create_darta(
        self,
        darta_data: dict,
        issued_by_user: int,
        file_path: str,
        receiver_office: int
    ) -> Darta:
        """
        Create and persist a new darta record.
        """
        new_darta = Darta(**darta_data)

        self.db.add(new_darta)
        self.db.commit()
        self.db.refresh(new_darta)

        return new_darta
    
    def get_dartas_by_filter(self, filters: dict) -> list[Darta]:
        """
        Retrieve dartas matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Darta)

        exact_filter = {
            "id" : Darta.id,
            "darta_id" : Darta.darta_id,
            "issused_by_user" : Darta.issued_by_user,
            "financial_year" : Darta.financial_year,
            "receiver_office" : Darta.receiver_office,
            "receiver_officer" : Darta.receiver_officer,
            "receiver_department" : Darta.receiver_department
        }

        ilike_filter = {
            "sender" : Darta.sender,
            "sender_email" : Darta.sender_email,
            "sender_contact_number" : Darta.sender_contact_number,
            "topic" : Darta.topic,
        }

        for key, column in exact_filter.items():
            if (value := filters.get(key)) is not None:
                query = query.filter(column == value)

        for key, column in ilike_filter.items():
            if (value := filters.get(key)) is not None:
                query = query.filter(column.ilike(f"%{value}%"))

        if filters.get("start_date") is not None:
            query = query.filter(Darta.darta_date >= filters["start_date"])

        if filters.get("end_date") is not None:
            query = query.filter(Darta.darta_date <= filters["end_date"])

        order_col = DARTA_ORDER_MAP.get(filters.get("order_by"), Darta.id)
        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()
