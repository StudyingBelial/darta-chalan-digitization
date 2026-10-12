from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.app.db.models.darta import Darta
from backend.app.db.models.chalan import Chalan
from backend.app.db.models.users import Users
from backend.app.enums import PERMISSIONS
from backend.app.core.permissions import has_permission
from backend.app.core.exceptions import PermissionDeniedError
from backend.app.core.logger import logger

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionDeniedError(f"User does not have permission: {permission.value}")

    def advanced_search_darta(
        self,
        user: Users,
        query_text: str | None = None,
        sender: str | None = None,
        status: str | None = None,
        receiver_office: int | None = None,
        receiver_department: int | None = None,
        receiver_officer: int | None = None,
        financial_year_id: int | None = None,
        start_date_bs: str | None = None,
        end_date_bs: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Darta]:
        """
        Advanced Darta search with OCR text keyword matching and filter parameters.
        """
        self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        query = self.db.query(Darta)

        if query_text:
            search_pattern = f"%{query_text.strip()}%"
            query = query.filter(
                or_(
                    Darta.topic.ilike(search_pattern),
                    Darta.sender.ilike(search_pattern),
                    Darta.sender_email.ilike(search_pattern),
                    Darta.extracted_ocr_text.ilike(search_pattern),
                    Darta.file_name.ilike(search_pattern)
                )
            )

        if sender:
            query = query.filter(Darta.sender.ilike(f"%{sender.strip()}%"))

        if status:
            query = query.filter(Darta.status == status.upper())

        if receiver_office:
            query = query.filter(Darta.receiver_office == receiver_office)

        if receiver_department:
            query = query.filter(Darta.receiver_department == receiver_department)

        if receiver_officer:
            query = query.filter(Darta.receiver_officer == receiver_officer)

        if financial_year_id:
            query = query.filter(Darta.financial_year == financial_year_id)

        if start_date_bs:
            query = query.filter(Darta.darta_date_bs >= start_date_bs)

        if end_date_bs:
            query = query.filter(Darta.darta_date_bs <= end_date_bs)

        results = query.order_by(Darta.id.desc()).offset(offset).limit(limit).all()
        logger.info(f"Advanced Darta search returned {len(results)} records for user {user.id}")
        return results

    def advanced_search_chalan(
        self,
        user: Users,
        query_text: str | None = None,
        receiver: str | None = None,
        status: str | None = None,
        sender_office: int | None = None,
        sender_department: int | None = None,
        sender_officer: int | None = None,
        start_date_bs: str | None = None,
        end_date_bs: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Chalan]:
        """
        Advanced Chalan search with OCR text keyword matching and filter parameters.
        """
        self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)
        query = self.db.query(Chalan)

        if query_text:
            search_pattern = f"%{query_text.strip()}%"
            query = query.filter(
                or_(
                    Chalan.topic.ilike(search_pattern),
                    Chalan.receiver.ilike(search_pattern),
                    Chalan.receiver_email.ilike(search_pattern),
                    Chalan.extracted_ocr_text.ilike(search_pattern),
                    Chalan.file_name.ilike(search_pattern)
                )
            )

        if receiver:
            query = query.filter(Chalan.receiver.ilike(f"%{receiver.strip()}%"))

        if status:
            query = query.filter(Chalan.status == status.upper())

        if sender_office:
            query = query.filter(Chalan.sender_office == sender_office)

        if sender_department:
            query = query.filter(Chalan.sender_department == sender_department)

        if sender_officer:
            query = query.filter(Chalan.sender_officer == sender_officer)

        if start_date_bs:
            query = query.filter(Chalan.chalan_date_bs >= start_date_bs)

        if end_date_bs:
            query = query.filter(Chalan.chalan_date_bs <= end_date_bs)

        results = query.order_by(Chalan.id.desc()).offset(offset).limit(limit).all()
        logger.info(f"Advanced Chalan search returned {len(results)} records for user {user.id}")
        return results
