class DartaChalanException(Exception):
    """Base exception for Darta-Chalan Digitization System"""
    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)

class DocumentNotFoundError(DartaChalanException):
    """Raised when a requested Darta or Chalan document is not found"""
    def __init__(self, document_id: int, document_type: str = "Document"):
        super().__init__(f"{document_type} with ID {document_id} was not found.")

class SequenceGenerationError(DartaChalanException):
    """Raised when failing to generate a sequential registration number"""
    pass

class OCRProcessingError(DartaChalanException):
    """Raised when OCR extraction encounters an unrecoverable failure"""
    pass

class StorageError(DartaChalanException):
    """Raised when file storage, upload validation, or retrieval fails"""
    pass

class InvalidBSDateError(DartaChalanException):
    """Raised when an invalid Bikram Sambat date is provided or conversion fails"""
    pass

class PermissionDeniedError(DartaChalanException):
    """Raised when a user attempts an unauthorized operation"""
    pass
