from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.forwarding import ForwardingCreate, ForwardingResponse
from backend.app.controllers.forwarding import ForwardingController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/forwarding", tags=["Document Forwarding"])

@router.post("", response_model=ForwardingResponse)
async def create_forwarding(
    forwarding_data: ForwardingCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ForwardingController.create_forwarding(forwarding_data, current_user, db)

@router.get("/{forwarding_id}", response_model=ForwardingResponse)
async def get_forwarding_by_id(
    forwarding_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ForwardingController.get_forwarding_by_id(forwarding_id, current_user, db)

@router.get("/document/{document_type}/{document_id}", response_model=List[ForwardingResponse])
async def get_document_forwarding_history(
    document_type: str,
    document_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ForwardingController.get_document_forwarding_history(document_type, document_id, current_user, db)
