from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.schemas.logs import LogResponse, FilteredLogSearch
from backend.app.controllers.logs import LogsController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/logs", tags=["Audit Logs"])

@router.get("", response_model=List[LogResponse])
async def get_logs(
    filter_params: FilteredLogSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await LogsController.get_logs(filter_params, current_user, db)
