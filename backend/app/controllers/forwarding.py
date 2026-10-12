from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.schemas.forwarding import ForwardingCreate
from backend.app.services.forwarding_service import ForwardingService
from backend.app.repositories.forwarding import ForwardingRepository
from backend.app.db.models.users import Users

class ForwardingController:
    @staticmethod
    async def create_forwarding(forwarding_data: ForwardingCreate, current_user: Users, db: Session):
        service = ForwardingService(db)
        return service.forward_document(
            user=current_user,
            document_type=forwarding_data.document_type,
            document_id=forwarding_data.document_id,
            target_office=forwarding_data.forwarded_to_office,
            target_department=forwarding_data.forwarded_to_department,
            target_officer=forwarding_data.forwarded_to_officer,
            remarks=forwarding_data.remarks
        )

    @staticmethod
    async def get_forwarding_by_id(forwarding_id: int, current_user: Users, db: Session):
        repo = ForwardingRepository(db)
        record = repo.get_forwarding_by_id(forwarding_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forwarding record #{forwarding_id} not found"
            )
        return record

    @staticmethod
    async def get_document_forwarding_history(document_type: str, document_id: int, current_user: Users, db: Session):
        service = ForwardingService(db)
        return service.get_forwarding_history(current_user, document_type, document_id)
