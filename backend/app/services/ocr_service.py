import os
from backend.app.core.config import settings
from backend.app.core.logger import logger

try:
    from PIL import Image
    import pytesseract
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
except ImportError:
    Image = None
    pytesseract = None

class OCRService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Perform OCR text extraction on an image file (PNG, JPG, TIFF, BMP).
        Returns extracted text string. Degrades gracefully if Tesseract/Pillow are not installed.
        """
        if not os.path.exists(file_path):
            logger.warning(f"OCR file path does not exist: {file_path}")
            return ""

        if not Image or not pytesseract:
            logger.warning("Pillow or pytesseract module not installed. OCR text extraction skipped.")
            return ""

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
            logger.info(f"Skipping OCR for file type '{ext}' (OCR active only for image types).")
            return ""

        try:
            image = Image.open(file_path)
            # Perform OCR (support English + Nepali if available)
            extracted_text = pytesseract.image_to_string(image, lang="eng+nep")
            cleaned_text = extracted_text.strip()
            logger.info(f"OCR successfully extracted {len(cleaned_text)} characters from {file_path}")
            return cleaned_text
        except Exception as e:
            logger.warning(f"OCR extraction failed for {file_path}: {e}")
            return ""
