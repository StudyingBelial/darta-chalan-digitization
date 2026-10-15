from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from backend.app.db.models.inbound_document import InboundDocument

class InboundDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[InboundDocument]:
        return self.db.query(InboundDocument).filter(InboundDocument.id == id).first()

    def create(self, data: Dict[str, Any]) -> InboundDocument:
        doc = InboundDocument(**data)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def update(self, id: int, data: Dict[str, Any]) -> Optional[InboundDocument]:
        doc = self.get_by_id(id)
        if not doc:
            return None
        for key, value in data.items():
            setattr(doc, key, value)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_documents(
        self,
        status: Optional[str] = None,
        source: Optional[str] = None,
        parsing_status: Optional[str] = None,
        search: Optional[str] = None,
        office_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[InboundDocument]:
        query = self.db.query(InboundDocument)

        if status:
            query = query.filter(InboundDocument.status == status)
        if source:
            query = query.filter(InboundDocument.source == source)
        if parsing_status:
            query = query.filter(InboundDocument.parsing_status == parsing_status)
        if office_id:
            query = query.filter((InboundDocument.target_office_id == office_id) | (InboundDocument.target_office_id.is_(None)))
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (InboundDocument.sender_name.ilike(search_pattern)) |
                (InboundDocument.sender_email.ilike(search_pattern)) |
                (InboundDocument.subject.ilike(search_pattern)) |
                (InboundDocument.file_name.ilike(search_pattern))
            )

        return query.order_by(InboundDocument.received_at.desc()).offset(offset).limit(limit).all()

    def count_documents(
        self,
        status: Optional[str] = None,
        office_id: Optional[int] = None
    ) -> int:
        query = self.db.query(InboundDocument)
        if status:
            query = query.filter(InboundDocument.status == status)
        if office_id:
            query = query.filter((InboundDocument.target_office_id == office_id) | (InboundDocument.target_office_id.is_(None)))
        return query.count()
