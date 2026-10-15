from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.controllers.system import SystemController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
async def get_health_status():
    return await SystemController.get_health_status()

@router.get("/stats")
async def get_system_stats(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await SystemController.get_system_stats(current_user, db)
