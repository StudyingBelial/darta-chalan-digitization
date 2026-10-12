import os
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Optional

from backend.app.schemas.inbound import (
    InboundDocumentResponse,
    InboundDocumentFilter,
    ConvertInboundToDarta,
    SimulateEmailRequest,
    ParsedCandidateFields,
    SMTPScannerStatusResponse,
    SMTPTestEmailRequest,
    SMTPToggleRequest
)
from backend.app.schemas.darta import DartaResponse
from backend.app.services.inbound_service import InboundService
from backend.app.services.parsing_service import DocumentParsingService
from backend.app.services.storage_service import StorageService
from backend.app.services.smtp_scanner import smtp_scanner_service
from backend.app.db.models.users import Users
from backend.app.core.exceptions import StorageError, PermissionDeniedError
from backend.app.enums import USER_TYPE

class InboundController:
    @staticmethod
    async def list_inbound_documents(
        filter_params: InboundDocumentFilter,
        current_user: Users,
        db: Session
    ) -> List[InboundDocumentResponse]:
        inbound_service = InboundService(db)
        docs = inbound_service.inbound_repo.list_documents(
            status=filter_params.status,
            source=filter_params.source,
            parsing_status=filter_params.parsing_status,
            search=filter_params.search,
            office_id=current_user.user_office,
            limit=filter_params.limit or 50,
            offset=filter_params.offset or 0
        )
        return [InboundDocumentResponse.model_validate(d) for d in docs]

    @staticmethod
    async def get_inbound_document(
        inbound_id: int,
        current_user: Users,
        db: Session
    ) -> InboundDocumentResponse:
        inbound_service = InboundService(db)
        doc = inbound_service.inbound_repo.get_by_id(inbound_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Inbound document #{inbound_id} not found.")
        return InboundDocumentResponse.model_validate(doc)

    @staticmethod
    async def parse_inbound_document(
        inbound_id: int,
        current_user: Users,
        db: Session
    ) -> InboundDocumentResponse:
        inbound_service = InboundService(db)
        try:
            doc = inbound_service.parse_inbound_document(inbound_id)
            return InboundDocumentResponse.model_validate(doc)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing document: {str(e)}")

    @staticmethod
    async def parse_uploaded_file(
        file: UploadFile,
        db: Session
    ) -> ParsedCandidateFields:
        """
        Parse an uploaded or scanned file on-the-fly without requiring immediate registration.
        """
        file_bytes = await file.read()
        storage_service = StorageService()
        storage_info = storage_service.save_file(
            file_content=file_bytes,
            original_filename=file.filename or "scanned_document.pdf",
            document_type="temp_parse"
        )
        
        parsing_service = DocumentParsingService(db)
        try:
            candidate_fields = parsing_service.parse_file(storage_info["file_path"])
            return candidate_fields
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to auto-parse file: {str(e)}")

    @staticmethod
    async def convert_inbound_to_darta(
        inbound_id: int,
        payload: ConvertInboundToDarta,
        current_user: Users,
        db: Session
    ) -> DartaResponse:
        inbound_service = InboundService(db)
        try:
            darta = inbound_service.convert_to_darta(
                inbound_id=inbound_id,
                darta_payload=payload,
                current_user=current_user
            )
            return DartaResponse.model_validate(darta)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to convert inbound to Darta: {str(e)}")

    @staticmethod
    async def simulate_incoming_email(
        payload: SimulateEmailRequest,
        current_user: Users,
        db: Session
    ) -> InboundDocumentResponse:
        inbound_service = InboundService(db)
        
        # If no file content provided, generate standard mock official letter PDF bytes
        import base64
        if payload.file_content_base64:
            file_bytes = base64.b64decode(payload.file_content_base64)
        else:
            # Minimal mock PDF with clear text for OCR testing
            file_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"

        doc = inbound_service.receive_inbound_document(
            file_bytes=file_bytes,
            file_name=payload.file_name or "incoming_directive.pdf",
            source="SMTP_EMAIL",
            sender_email=payload.sender_email,
            sender_name=payload.sender_name,
            subject=payload.subject,
            target_office_id=payload.target_office_id or current_user.user_office,
            auto_parse=True
        )
        return InboundDocumentResponse.model_validate(doc)

    @staticmethod
    async def download_inbound_file(
        inbound_id: int,
        current_user: Users,
        db: Session
    ):
        inbound_service = InboundService(db)
        doc = inbound_service.inbound_repo.get_by_id(inbound_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Inbound document #{inbound_id} not found.")

        if not doc.file_path or not os.path.exists(doc.file_path):
            raise StorageError(f"File for inbound document #{inbound_id} not found on server.")

        storage_service = StorageService()
        mime_type = storage_service.get_mime_type(doc.file_path)
        filename = doc.file_name or os.path.basename(doc.file_path)

        return FileResponse(
            path=doc.file_path,
            filename=filename,
            media_type=mime_type
        )

    @staticmethod
    async def get_smtp_status(current_user: Users) -> SMTPScannerStatusResponse:
        """Get diagnostic status and telemetry of the inbound SMTP scanner listener."""
        status_dict = smtp_scanner_service.get_status()
        return SMTPScannerStatusResponse(**status_dict)

    @staticmethod
    async def send_smtp_test_email(
        payload: SMTPTestEmailRequest,
        current_user: Users
    ) -> dict:
        """
        Send a test email with attached PDF over loopback ESMTP to test the end-to-end scanner pipeline.
        """
        try:
            result = await smtp_scanner_service.send_test_email(
                sender_email=payload.sender_email or "scanner.canon@ntc.net.np",
                sender_name=payload.sender_name or "Canon imageRUNNER 2520",
                subject=payload.subject or "Scanned Document via SMTP",
                file_name=payload.file_name or "canon_scan.pdf"
            )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to dispatch test SMTP scan: {str(e)}"
            )

    @staticmethod
    async def toggle_smtp_scanner(
        payload: SMTPToggleRequest,
        current_user: Users
    ) -> SMTPScannerStatusResponse:
        """Start or stop the SMTP scanner listener dynamically (Admin only)."""
        if current_user.user_type not in (USER_TYPE.SYSTEM_ADMIN, USER_TYPE.OFFICE_ADMIN):
            raise PermissionDeniedError("Only administrators can toggle the hardware scanner listener.")

        if payload.enable:
            success = await smtp_scanner_service.start()
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Could not start SMTP Scanner: {smtp_scanner_service.last_error}"
                )
        else:
            await smtp_scanner_service.stop()

        status_dict = smtp_scanner_service.get_status()
        return SMTPScannerStatusResponse(**status_dict)
