import os
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from backend.app.schemas.chalan import CreateChalan, FilterChalanSearch
from backend.app.services.document_workflow import DocumentWorkflowService
from backend.app.services.storage_service import StorageService
from backend.app.services.ocr_service import OCRService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import DocumentNotFoundError, StorageError

class ChalanController:
    @staticmethod
    async def create_chalan(chalan_data: CreateChalan, file: UploadFile, current_user: Users, db: Session):
        file_bytes = await file.read()
        storage_service = StorageService()
        storage_info = storage_service.save_file(
            file_content=file_bytes,
            original_filename=file.filename or "uploaded_document.pdf",
            document_type="chalan"
        )
        
        workflow_service = DocumentWorkflowService(db)
        chalan = workflow_service.create_chalan(
            user=current_user,
            chalan_data=chalan_data,
            file_path=storage_info["file_path"]
        )
        return chalan

    @staticmethod
    async def get_chalan_by_id(chalan_id: int, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        chalan = workflow_service.get_chalan_by_id(current_user, chalan_id)
        if not chalan:
            raise DocumentNotFoundError(chalan_id, "Chalan")
        return chalan

    @staticmethod
    async def search_chalan(filter_params: FilterChalanSearch, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        return workflow_service.search_chalans(current_user, filter_params)

    @staticmethod
    async def run_ocr(chalan_id: int, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        chalan = workflow_service.get_chalan_by_id(current_user, chalan_id)
        if not chalan:
            raise DocumentNotFoundError(chalan_id, "Chalan")

        if not chalan.file_path or not os.path.exists(chalan.file_path):
            raise StorageError(f"Attachment file for Chalan #{chalan_id} does not exist on disk.")

        ocr_text = OCRService.extract_text(chalan.file_path)
        updated = workflow_service.update_chalan(current_user, chalan_id, {"extracted_ocr_text": ocr_text})
        return {
            "chalan_id": chalan_id,
            "extracted_text": ocr_text,
            "message": "OCR extraction completed successfully"
        }

    @staticmethod
    async def download_file(chalan_id: int, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        chalan = workflow_service.get_chalan_by_id(current_user, chalan_id)
        if not chalan:
            raise DocumentNotFoundError(chalan_id, "Chalan")

        if not chalan.file_path or not os.path.exists(chalan.file_path):
            raise StorageError(f"Attachment file for Chalan #{chalan_id} not found on server.")

        storage_service = StorageService()
        mime_type = storage_service.get_mime_type(chalan.file_path)
        filename = chalan.file_name or os.path.basename(chalan.file_path)

        return FileResponse(
            path=chalan.file_path,
            filename=filename,
            media_type=mime_type
        )
