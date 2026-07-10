from sqlalchemy.orm import Session

from backend.app.db import Chalan

CHALAN_ORDER_MAP = {
    "id" : Chalan.id,
    "chalan_id" : Chalan.chalan_id,
    "issued_by_user" : Chalan.issued_by_user,
    "sender_email" : Chalan.sender_email,
    "receiver" : Chalan.receiver,
    "receiver_email" : Chalan.receiver_email,
    "receiver_contact_number" : Chalan.receiver_contact_number,
    "chalan_date" : Chalan.chalan_date,
    "topic" : Chalan.topic,
    "file_name" : Chalan.file_name,
    "timestamp" : Chalan.timestamp,
    "file_path" : Chalan.file_path,
    "sender_office" : Chalan.sender_office,
    "sender_department" : Chalan.sender_department,
    "sender_officer" : Chalan.sender_office
}

class ChalanRepository:
    def __init__(self, db: Session):
        """
        Initialize the chalan repository with a database session.
        """
        self.db = db

    def get_chalan_by_id(self, id: int) -> Chalan | None:
        """
        Retrieve a chalan from the database by its primary key ID.
        """
        return self.db.get(Chalan, id)

    def get_chalan_by_chalan_id(self, chalan_id: int) -> list[Chalan]:
        """
        Retrieve chalans matching the register/reference chalan_id.
        """
        return self.db.query(Chalan).filter(Chalan.chalan_id == chalan_id).all()

    def create_chalan(
        self,
        chalan_data: dict,
        issued_by_user: int,
        file_path: str,
        sender_office: int
    ) -> Chalan:
        """
        Create and persist a new chalan record.
        """
        chalan_data.update({
            "issued_by_user": issued_by_user,
            "file_path" : file_path,
            "sender_office" : sender_office,
        })
        new_chalan = Chalan(chalan_data)

        self.db.add(new_chalan)
        self.db.commit()
        self.db.refresh(new_chalan)

        return new_chalan
    
    def get_chalans_by_filter(self, filters: dict) -> list[Chalan]:
        """
        Retrieve chalans matching search filters, sorted and limited to 100 entries.
        """
        query = self.db.query(Chalan)

        exact_filters = {
            "id" : Chalan.id,
            "chalan_id" : Chalan.chalan_id,
            "issued_by_user" : Chalan.issued_by_user,
            "sender_office" : Chalan.sender_office,
            "sender_department" : Chalan.sender_department,
            "sender_officer" : Chalan.sender_officer
        }

        ilike_filters = {
            "sender_email" : Chalan.sender_email,
            "receiver" : Chalan.receiver,
            "receiver_email" : Chalan.receiver_email,
            "receiver_contact_number" : Chalan.receiver_contact_number,
            "topic" : Chalan.topic
        }
        
        for key, column in exact_filters.items():
            if (value := filters.get(key)) is not None:
                query = query.filter(column == value)

        for key, column in ilike_filters.items():
            if (value := filters.get(key)) is not None:
                query = query.filter(column.ilike(f"%{value}%"))

        if filters.get("start_date") is not None:
            query = query.filter(Chalan.chalan_date >= filters["start_date"])

        if filters.get("end_date") is not None:
            query = query.filter(Chalan.chalan_date <= filters["end_date"])

        order_col = CHALAN_ORDER_MAP.get(filters.get("order_by"), Chalan.id)
        direction = filters.get("order_direction", "desc")

        if direction == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        return query.limit(100).all()