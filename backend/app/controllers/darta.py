import os
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from backend.app.schemas.darta import CreateDarta, FilterDartaSearch
from backend.app.services.document_workflow import DocumentWorkflowService
from backend.app.services.storage_service import StorageService
from backend.app.services.ocr_service import OCRService
from backend.app.db.models.users import Users
from backend.app.core.exceptions import DocumentNotFoundError, StorageError

class DartaController:
    @staticmethod
    async def create_darta(darta_data: CreateDarta, file: UploadFile, current_user: Users, db: Session):
        file_bytes = await file.read()
        storage_service = StorageService()
        storage_info = storage_service.save_file(
            file_content=file_bytes,
            original_filename=file.filename or "uploaded_document.pdf",
            document_type="darta"
        )
        
        workflow_service = DocumentWorkflowService(db)
        darta = workflow_service.create_darta(
            user=current_user,
            darta_data=darta_data,
            file_path=storage_info["file_path"]
        )
        return darta

    @staticmethod
    async def get_darta_by_id(darta_id: int, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        darta = workflow_service.get_darta_by_id(current_user, darta_id)
        if not darta:
            raise DocumentNotFoundError(darta_id, "Darta")
        return darta

    @staticmethod
    async def search_darta(filter_params: FilterDartaSearch, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        return workflow_service.search_dartas(current_user, filter_params)

    @staticmethod
    async def run_ocr(darta_id: int, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        darta = workflow_service.get_darta_by_id(current_user, darta_id)
        if not darta:
            raise DocumentNotFoundError(darta_id, "Darta")

        if not darta.file_path or not os.path.exists(darta.file_path):
            raise StorageError(f"Attachment file for Darta #{darta_id} does not exist on disk.")

        ocr_text = OCRService.extract_text(darta.file_path)
        updated = workflow_service.update_darta(current_user, darta_id, {"extracted_ocr_text": ocr_text})
        return {
            "darta_id": darta_id,
            "extracted_text": ocr_text,
            "message": "OCR extraction completed successfully"
        }

    @staticmethod
    async def download_file(darta_id: int, current_user: Users, db: Session):
        workflow_service = DocumentWorkflowService(db)
        darta = workflow_service.get_darta_by_id(current_user, darta_id)
        if not darta:
            raise DocumentNotFoundError(darta_id, "Darta")

        if not darta.file_path or not os.path.exists(darta.file_path):
            raise StorageError(f"Attachment file for Darta #{darta_id} not found on server.")

        storage_service = StorageService()
        mime_type = storage_service.get_mime_type(darta.file_path)
        filename = darta.file_name or os.path.basename(darta.file_path)

        return FileResponse(
            path=darta.file_path,
            filename=filename,
            media_type=mime_type
        )
