import csv
import io
from sqlalchemy.orm import Session
from backend.app.db.models.darta import Darta
from backend.app.db.models.chalan import Chalan
from backend.app.db.models.users import Users
from backend.app.enums import PERMISSIONS
from backend.app.core.permissions import has_permission
from backend.app.core.exceptions import PermissionDeniedError
from backend.app.services.search_service import SearchService

class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self.search_service = SearchService(db)

    def _check_permission(self, user: Users, permission: PERMISSIONS):
        if not has_permission(user, permission):
            raise PermissionDeniedError(f"User does not have permission: {permission.value}")

    def export_darta_register_csv(
        self,
        user: Users,
        receiver_office: int | None = None,
        financial_year_id: int | None = None,
        start_date_bs: str | None = None,
        end_date_bs: str | None = None
    ) -> str:
        """
        Generate CSV export string for official Darta Register (दर्ता किताब).
        """
        self._check_permission(user, PERMISSIONS.DARTA_SEARCH)
        dartas = self.search_service.advanced_search_darta(
            user=user,
            receiver_office=receiver_office,
            financial_year_id=financial_year_id,
            start_date_bs=start_date_bs,
            end_date_bs=end_date_bs,
            limit=10000
        )

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers in Nepali & English format for official compliance
        writer.writerow([
            "System ID",
            "Darta No (दर्ता नं)",
            "Darta Date (AD)",
            "Darta Date (BS)",
            "Sender (पठाउने निकाय/व्यक्ति)",
            "Sender Email",
            "Contact No",
            "Subject/Topic (विषय)",
            "Status",
            "Receiver Office ID",
            "Registration Timestamp"
        ])

        for d in dartas:
            writer.writerow([
                d.id,
                d.darta_id,
                d.darta_date.strftime("%Y-%m-%d") if d.darta_date else "",
                d.darta_date_bs or "",
                d.sender,
                d.sender_email,
                d.sender_contact_number or "",
                d.topic,
                d.status,
                d.receiver_office or "",
                d.timestamp.strftime("%Y-%m-%d %H:%M:%S") if d.timestamp else ""
            ])

        return output.getvalue()

    def export_chalan_register_csv(
        self,
        user: Users,
        sender_office: int | None = None,
        start_date_bs: str | None = None,
        end_date_bs: str | None = None
    ) -> str:
        """
        Generate CSV export string for official Chalan Register (चलानी किताब).
        """
        self._check_permission(user, PERMISSIONS.CHALAN_SEARCH)
        chalans = self.search_service.advanced_search_chalan(
            user=user,
            sender_office=sender_office,
            start_date_bs=start_date_bs,
            end_date_bs=end_date_bs,
            limit=10000
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # Headers in Nepali & English format for official compliance
        writer.writerow([
            "System ID",
            "Chalan No (चलानी नं)",
            "Chalan Date (AD)",
            "Chalan Date (BS)",
            "Receiver (पाउने निकाय/व्यक्ति)",
            "Receiver Email",
            "Contact No",
            "Subject/Topic (विषय)",
            "Status",
            "Sender Office ID",
            "Dispatch Timestamp"
        ])

        for c in chalans:
            writer.writerow([
                c.id,
                c.chalan_id,
                c.chalan_date.strftime("%Y-%m-%d") if c.chalan_date else "",
                c.chalan_date_bs or "",
                c.receiver,
                c.receiver_email,
                c.receiver_contact_number or "",
                c.topic or "",
                c.status,
                c.sender_office or "",
                c.timestamp.strftime("%Y-%m-%d %H:%M:%S") if c.timestamp else ""
            ])

        return output.getvalue()
