import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from backend.app.core.config import settings
from backend.app.core.exceptions import StorageError
from backend.app.core.logger import logger

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

class StorageService:
    def __init__(self, base_upload_dir: str | None = None):
        self.base_upload_dir = base_upload_dir or settings.UPLOAD_DIR
        os.makedirs(self.base_upload_dir, exist_ok=True)

    @staticmethod
    def calculate_bytes_hash(file_content: bytes) -> str:
        """
        Calculate SHA-256 hash string for raw file bytes.
        """
        return hashlib.sha256(file_content).hexdigest()

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash string for a stored file on disk.
        """
        if not os.path.exists(file_path):
            raise StorageError(f"File not found for hash calculation: {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify if a file's SHA-256 hash matches the expected hash value.
        """
        if not expected_hash:
            return False
        current_hash = self.calculate_file_hash(file_path)
        return current_hash.lower() == expected_hash.lower()

    def save_file(self, file_content: bytes, original_filename: str, document_type: str = "darta") -> dict:
        """
        Validate and save uploaded file to directory hierarchy: /storage/uploads/{doc_type}/{YYYY}/{MM}/{unique_filename}
        Returns dict with file_name, file_path, file_size, extension, and file_hash.
        """
        if not file_content:
            raise StorageError("Uploaded file is empty.")

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_content) > max_bytes:
            raise StorageError(f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB.")

        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise StorageError(f"File extension '{ext}' is not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

        now = datetime.now()
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")
        
        target_dir = os.path.join(self.base_upload_dir, document_type.lower(), year_str, month_str)
        os.makedirs(target_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{now.strftime('%Y%m%d%H%M%S')}{ext}"
        target_path = os.path.join(target_dir, unique_filename)

        try:
            with open(target_path, "wb") as f:
                f.write(file_content)
            logger.info(f"Saved {document_type} file: {target_path} ({len(file_content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to write file {target_path}: {e}")
            raise StorageError(f"Failed to save file on server: {e}")

        file_hash = self.calculate_bytes_hash(file_content)

        return {
            "file_name": original_filename,
            "stored_filename": unique_filename,
            "file_path": os.path.abspath(target_path),
            "file_size": len(file_content),
            "extension": ext,
            "file_hash": file_hash
        }

    def delete_file(self, file_path: str) -> bool:
        """
        Safely delete a file from storage.
        """
        if not os.path.exists(file_path):
            logger.warning(f"Attempted to delete non-existent file: {file_path}")
            return False
            
        try:
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    def get_mime_type(self, file_path: str) -> str:
        """
        Get MIME type of a file.
        """
        mime, _ = mimetypes.guess_type(file_path)
        return mime or "application/octet-stream"
