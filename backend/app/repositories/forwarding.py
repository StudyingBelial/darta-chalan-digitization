from sqlalchemy.orm import Session
from backend.app.db.models.forwarding import DocumentForwarding

class ForwardingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_forwarding(self, forwarding_data: dict) -> DocumentForwarding:
        record = DocumentForwarding(**forwarding_data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_document(self, document_type: str, document_id: int) -> list[DocumentForwarding]:
        return (
            self.db.query(DocumentForwarding)
            .filter(
                DocumentForwarding.document_type == document_type.upper(),
                DocumentForwarding.document_id == document_id
            )
            .order_by(DocumentForwarding.timestamp.desc())
            .all()
        )
