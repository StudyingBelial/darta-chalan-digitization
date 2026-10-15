from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.darta import FilterDartaSearch
from backend.app.schemas.chalan import FilterChalanSearch
from backend.app.controllers.export import ExportController
from backend.app.core.dependencies import get_current_user
from backend.app.db.base import get_db
from backend.app.db.models.users import Users

router = APIRouter(prefix="/export", tags=["Exports"])

@router.get("/darta")
async def export_darta_csv(
    filter_params: FilterDartaSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ExportController.export_darta_csv(filter_params, current_user, db)

@router.get("/chalan")
async def export_chalan_csv(
    filter_params: FilterChalanSearch = Depends(),
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await ExportController.export_chalan_csv(filter_params, current_user, db)
