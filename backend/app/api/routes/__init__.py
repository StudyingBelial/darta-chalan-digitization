from fastapi import APIRouter
from backend.app.api.routes.authentication import router as auth_router
from backend.app.api.routes.users import router as users_router
from backend.app.api.routes.darta import router as darta_router
from backend.app.api.routes.chalan import router as chalan_router
from backend.app.api.routes.forwarding import router as forwarding_router
from backend.app.api.routes.offices import router as offices_router
from backend.app.api.routes.departments import router as departments_router
from backend.app.api.routes.officers import router as officers_router
from backend.app.api.routes.financial_year import router as fy_router
from backend.app.api.routes.logs import router as logs_router
from backend.app.api.routes.export import router as export_router
from backend.app.api.routes.system import router as system_router
from backend.app.api.routes.inbound import router as inbound_router
from backend.app.api.routes.notifications import router as notifications_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(darta_router)
api_router.include_router(chalan_router)
api_router.include_router(forwarding_router)
api_router.include_router(offices_router)
api_router.include_router(departments_router)
api_router.include_router(officers_router)
api_router.include_router(fy_router)
api_router.include_router(logs_router)
api_router.include_router(export_router)
api_router.include_router(system_router)
api_router.include_router(inbound_router)
api_router.include_router(notifications_router)
