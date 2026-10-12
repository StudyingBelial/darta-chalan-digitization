import os
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.app.db.models.inbound_document import InboundDocument
from backend.app.db.models.notification import Notification
from backend.app.db.models.users import Users
from backend.app.db.models.darta import Darta
from backend.app.repositories.inbound import InboundDocumentRepository
from backend.app.repositories.notification import NotificationRepository
from backend.app.services.storage_service import StorageService
from backend.app.services.parsing_service import DocumentParsingService
from backend.app.services.document_workflow import DocumentWorkflowService
from backend.app.services.audit_service import AuditLogService
from backend.app.schemas.darta import CreateDarta
from backend.app.schemas.inbound import ParsedCandidateFields, ConvertInboundToDarta
from backend.app.core.logger import logger
from backend.app.enums import LOG_TYPE, LOG_SOURCE

class InboundService:
    def __init__(self, db: Session):
        self.db = db
        self.inbound_repo = InboundDocumentRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.storage_service = StorageService()
        self.parsing_service = DocumentParsingService(db)
        self.workflow_service = DocumentWorkflowService(db)
        self.audit_service = AuditLogService(db)

    def receive_inbound_document(
        self,
        file_bytes: bytes,
        file_name: str,
        source: str = "SMTP_EMAIL",
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        subject: Optional[str] = None,
        target_office_id: Optional[int] = None,
        target_department_id: Optional[int] = None,
        auto_parse: bool = True
    ) -> InboundDocument:
        """
        Store an incoming document (via SMTP email, Canon scanner, or direct upload),
        optionally run automatic parsing, and generate persistent notification for employees.
        """
        # Save file to storage
        storage_info = self.storage_service.save_file(
            file_content=file_bytes,
            original_filename=file_name,
            document_type="inbound"
        )
        saved_file_path = storage_info["file_path"]

        parsed_data_dict = None
        confidence_score = 0.0
        parsing_status = "PENDING"

        if auto_parse:
            try:
                candidate_fields = self.parsing_service.parse_file(
                    file_path=saved_file_path,
                    metadata={"sender_email": sender_email, "sender_name": sender_name, "subject": subject}
                )
                parsed_data_dict = candidate_fields.model_dump()
                confidence_score = candidate_fields.confidence_score
                parsing_status = candidate_fields.parsing_status
            except Exception as e:
                logger.error(f"Auto-parsing error for inbound file {file_name}: {e}")
                parsing_status = "FAILED"

        # Create InboundDocument DB record
        inbound_data = {
            "source": source,
            "sender_email": sender_email,
            "sender_name": sender_name or "Unknown Sender",
            "subject": subject or "Incoming Document",
            "file_name": file_name,
            "file_path": saved_file_path,
            "parsed_data": parsed_data_dict,
            "confidence_score": confidence_score,
            "parsing_status": parsing_status,
            "status": "PENDING_REVIEW",
            "target_office_id": target_office_id,
            "target_department_id": target_department_id,
        }
        inbound_doc = self.inbound_repo.create(inbound_data)

        # Dispatch Notification to lower-level employees & office staff
        notif_title = f"New {source.replace('_', ' ').title()}: {subject or file_name}"
        notif_msg = (
            f"Received from {sender_name or sender_email or 'Scanner'}. "
            f"Confidence: {int(confidence_score * 100)}% ({parsing_status.replace('_', ' ')}). "
            f"Click to review and register into Darta."
        )
        self.notification_repo.create({
            "target_office_id": target_office_id,
            "target_role": "STAFF",
            "title": notif_title,
            "message": notif_msg,
            "notification_type": "INBOUND_EMAIL" if source == "SMTP_EMAIL" else "SCAN_INTAKE",
            "inbound_doc_id": inbound_doc.id,
            "action_url": f"/inbound?review_id={inbound_doc.id}"
        })

        # Audit log the intake event
        self.audit_service.log_event(
            message=f"Inbound document #{inbound_doc.id} received via {source} from '{sender_email or 'Scanner'}'",
            log_type=LOG_TYPE.INFO,
            source=LOG_SOURCE.SYSTEM,
            office_id=target_office_id
        )

        return inbound_doc

    def parse_inbound_document(self, inbound_id: int) -> InboundDocument:
        """
        Manually trigger/re-run parsing on an existing inbound document.
        """
        doc = self.inbound_repo.get_by_id(inbound_id)
        if not doc:
            raise ValueError(f"Inbound document #{inbound_id} not found")

        candidate_fields = self.parsing_service.parse_file(
            file_path=doc.file_path,
            metadata={"sender_email": doc.sender_email, "sender_name": doc.sender_name, "subject": doc.subject}
        )

        updated = self.inbound_repo.update(inbound_id, {
            "parsed_data": candidate_fields.model_dump(),
            "confidence_score": candidate_fields.confidence_score,
            "parsing_status": candidate_fields.parsing_status,
            "status": "PARSED" if doc.status == "PENDING_REVIEW" else doc.status
        })
        return updated

    def convert_to_darta(self, inbound_id: int, darta_payload: ConvertInboundToDarta, current_user: Users) -> Darta:
        """
        Convert a verified inbound document into an official Darta register record.
        """
        doc = self.inbound_repo.get_by_id(inbound_id)
        if not doc:
            raise ValueError(f"Inbound document #{inbound_id} not found")

        # Create Darta registration schema
        darta_data = CreateDarta(
            sender=darta_payload.sender,
            sender_email=darta_payload.sender_email,
            sender_contact_number=darta_payload.sender_contact_number,
            darta_date=darta_payload.darta_date,
            darta_date_bs=darta_payload.darta_date_bs,
            financial_year=darta_payload.financial_year,
            topic=darta_payload.topic,
            receiver_department=darta_payload.receiver_department,
            receiver_officer=darta_payload.receiver_officer,
            file_name=doc.file_name,
            status="REGISTERED"
        )

        # Call workflow service to create official Darta
        darta = self.workflow_service.create_darta(
            user=current_user,
            darta_data=darta_data,
            file_path=doc.file_path,
            receiver_office=doc.target_office_id or current_user.user_office
        )

        # Update inbound document status
        self.inbound_repo.update(inbound_id, {
            "status": "CONVERTED_TO_DARTA",
            "converted_darta_id": darta.id,
            "assigned_to_user_id": current_user.id
        })

        # Mark related notifications as read
        notifs = self.db.query(Notification).filter(Notification.inbound_doc_id == inbound_id).all()
        for n in notifs:
            n.is_read = True
        self.db.commit()

        return darta
