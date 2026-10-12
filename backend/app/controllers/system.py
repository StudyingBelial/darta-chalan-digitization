from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.core.config import settings
from backend.app.db.models.users import Users
from backend.app.db.models.darta import Darta
from backend.app.db.models.chalan import Chalan
from backend.app.db.models.offices import Offices

class SystemController:
    @staticmethod
    async def get_health_status():
        return {
            "status": "healthy",
            "system": settings.PROJECT_NAME,
            "version": settings.VERSION
        }

    @staticmethod
    async def get_system_stats(current_user: Users, db: Session):
        total_darta = db.query(func.count(Darta.id)).scalar() or 0
        total_chalan = db.query(func.count(Chalan.id)).scalar() or 0
        total_users = db.query(func.count(Users.id)).filter(Users.is_disabled == False).scalar() or 0
        total_offices = db.query(func.count(Offices.id)).scalar() or 0

        return {
            "system_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "statistics": {
                "total_darta_records": total_darta,
                "total_chalan_records": total_chalan,
                "active_user_accounts": total_users,
                "total_registered_offices": total_offices
            }
        }
