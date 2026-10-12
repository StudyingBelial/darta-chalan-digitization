import re
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, date

from backend.app.schemas.inbound import ParsedCandidateFields, FieldConfidence
from backend.app.services.ocr_service import OCRService
from backend.app.services.date_service import DateService
from backend.app.db.models.departments import Departments
from backend.app.db.models.officers import Officers
from backend.app.db.models.financial_year import FinancialYear
from backend.app.core.logger import logger

class BaseDocumentParser(ABC):
    """
    Abstract interface for document parsing engines.
    Allows easy plug-and-play of custom format guidelines, heuristic extractors, or LLM agents.
    """
    @abstractmethod
    def parse_text(self, text: str, db: Optional[Session] = None, metadata: Optional[Dict[str, Any]] = None) -> ParsedCandidateFields:
        pass


class HeuristicOCRDocumentParser(BaseDocumentParser):
    """
    Rule-based and heuristic document parser designed for Nepalese governmental
    and organizational incoming/outgoing correspondence.
    Computes individual field confidences and an overall weighted confidence score against a high threshold.
    """
    DEFAULT_THRESHOLD = 0.80  # Strict 80% confidence threshold

    def parse_text(self, text: str, db: Optional[Session] = None, metadata: Optional[Dict[str, Any]] = None) -> ParsedCandidateFields:
        metadata = metadata or {}
        field_confidences: Dict[str, FieldConfidence] = {}
        
        raw_text = text or ""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # 1. Extract Email Address
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        email_match = re.search(email_pattern, raw_text)
        detected_email = metadata.get("sender_email") or (email_match.group(0) if email_match else None)
        email_conf = 0.95 if detected_email else 0.0
        field_confidences["sender_email"] = FieldConfidence(
            value=detected_email,
            confidence=email_conf,
            is_high_confidence=email_conf >= self.DEFAULT_THRESHOLD,
            source="metadata" if metadata.get("sender_email") else "regex_extraction"
        )

        # 2. Extract Sender / Organization Name
        detected_sender = metadata.get("sender_name")
        sender_conf = 0.95 if detected_sender else 0.0
        if not detected_sender:
            # Check for standard prefixes: From:, प्रेषक:, Ministry, Department, Nepal Telecom, etc.
            sender_patterns = [
                r'(?:From|प्रेषक|Sender|कार्यालय|मन्त्रालय|संस्थान)\s*[:：\-]?\s*(.+)',
                r'((?:Government of Nepal|नेपाल सरकार|Ministry of [A-Za-z ]+|Department of [A-Za-z ]+|Nepal Telecom|NTC)[^\n,]*)'
            ]
            for pat in sender_patterns:
                match = re.search(pat, raw_text, re.IGNORECASE)
                if match:
                    detected_sender = match.group(1).strip()
                    sender_conf = 0.85
                    break
            
            if not detected_sender and lines:
                # Top lines usually contain the organization letterhead
                for line in lines[:3]:
                    if len(line) > 3 and not re.search(r'date|मिति|page|पत्र', line, re.I):
                        detected_sender = line
                        sender_conf = 0.65
                        break

        field_confidences["sender"] = FieldConfidence(
            value=detected_sender,
            confidence=sender_conf,
            is_high_confidence=sender_conf >= self.DEFAULT_THRESHOLD,
            source="heuristic_letterhead"
        )

        # 3. Extract Contact Number
        phone_pattern = r'(?:\+?977[- ]?)?(?:9[78]\d{8}|01-\d{6,7}|\b\d{10}\b)'
        phone_match = re.search(phone_pattern, raw_text)
        detected_phone = phone_match.group(0) if phone_match else None
        phone_conf = 0.90 if detected_phone else 0.0
        field_confidences["sender_contact_number"] = FieldConfidence(
            value=detected_phone,
            confidence=phone_conf,
            is_high_confidence=phone_conf >= self.DEFAULT_THRESHOLD,
            source="regex_phone"
        )

        # 4. Extract Dates (Gregorian AD and Bikram Sambat BS)
        detected_date_ad = None
        detected_date_bs = None
        date_conf = 0.0

        # Look for BS year (e.g. 2080, 2081, 2082)
        bs_pattern = r'\b(208[0-9])[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[0-2])\b'
        bs_match = re.search(bs_pattern, raw_text)
        if bs_match:
            detected_date_bs = f"{bs_match.group(1)}-{bs_match.group(2)}-{bs_match.group(3)}"
            date_conf = 0.90
            try:
                detected_date_ad = str(DateService.bs_to_ad(detected_date_bs))
            except Exception:
                pass

        # Look for AD date (e.g. 2024-08-25, 2025-01-15, 2026-08-25)
        if not detected_date_ad:
            ad_pattern = r'\b(202[0-9])[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[01])\b'
            ad_match = re.search(ad_pattern, raw_text)
            if ad_match:
                detected_date_ad = f"{ad_match.group(1)}-{ad_match.group(2)}-{ad_match.group(3)}"
                date_conf = 0.85
                try:
                    detected_date_bs = DateService.ad_to_bs(datetime.strptime(detected_date_ad, "%Y-%m-%d").date())
                except Exception:
                    pass

        if not detected_date_ad:
            # Fallback to today's date
            detected_date_ad = date.today().isoformat()
            try:
                detected_date_bs = DateService.ad_to_bs(date.today())
            except Exception:
                detected_date_bs = "2081-05-09"
            date_conf = 0.40

        field_confidences["darta_date"] = FieldConfidence(
            value=detected_date_ad,
            confidence=date_conf,
            is_high_confidence=date_conf >= self.DEFAULT_THRESHOLD,
            source="date_parser"
        )
        field_confidences["darta_date_bs"] = FieldConfidence(
            value=detected_date_bs,
            confidence=date_conf,
            is_high_confidence=date_conf >= self.DEFAULT_THRESHOLD,
            source="nepali_date_conversion"
        )

        # 5. Extract Subject / Topic
        detected_topic = metadata.get("subject")
        topic_conf = 0.95 if detected_topic else 0.0
        if not detected_topic:
            topic_patterns = [
                r'(?:Subject|विषय|Regarding|Re|प्रसङ्ग)\s*[:：\-]\s*(.+)',
                r'(?:Subject|विषय)\s+(.+)'
            ]
            for pat in topic_patterns:
                match = re.search(pat, raw_text, re.IGNORECASE)
                if match:
                    detected_topic = match.group(1).strip()
                    topic_conf = 0.85
                    break
            
            if not detected_topic and len(lines) > 1:
                # Find line with meaningful content
                for line in lines[1:6]:
                    if len(line) > 15 and not re.search(r'date|email|phone|tel|मिति', line, re.I):
                        detected_topic = line
                        topic_conf = 0.55
                        break

        field_confidences["topic"] = FieldConfidence(
            value=detected_topic,
            confidence=topic_conf,
            is_high_confidence=topic_conf >= self.DEFAULT_THRESHOLD,
            source="subject_extractor"
        )

        # 6. Match Target Department & Financial Year from Database
        suggested_dept_id = None
        suggested_dept_name = None
        dept_conf = 0.0
        suggested_officer_id = None
        suggested_officer_name = None
        fy_id = 1

        if db:
            try:
                # Department match
                departments = db.query(Departments).filter(Departments.is_disabled == False).all()
                for dept in departments:
                    if dept.name.lower() in raw_text.lower():
                        suggested_dept_id = dept.id
                        suggested_dept_name = dept.name
                        dept_conf = 0.85
                        break
                
                # Officer match
                if suggested_dept_id:
                    officer = db.query(Officers).filter(Officers.department == suggested_dept_id, Officers.is_disabled == False).first()
                    if officer:
                        suggested_officer_id = officer.id
                        suggested_officer_name = officer.name

                # FY match
                fy = db.query(FinancialYear).order_by(FinancialYear.id.desc()).first()
                if fy:
                    fy_id = fy.id
            except Exception as e:
                logger.warning(f"Error querying DB for parsing matches: {e}")

        field_confidences["receiver_department"] = FieldConfidence(
            value=suggested_dept_id,
            confidence=dept_conf,
            is_high_confidence=dept_conf >= self.DEFAULT_THRESHOLD,
            source="keyword_taxonomy_match"
        )

        # 7. Calculate Weighted Aggregate Confidence Score
        weights = {
            "sender": 0.25,
            "sender_email": 0.20,
            "topic": 0.30,
            "darta_date": 0.15,
            "receiver_department": 0.10
        }
        
        total_score = (
            weights["sender"] * sender_conf +
            weights["sender_email"] * email_conf +
            weights["topic"] * topic_conf +
            weights["darta_date"] * date_conf +
            weights["receiver_department"] * dept_conf
        )
        total_score = round(min(max(total_score, 0.0), 1.0), 2)

        # High Threshold Evaluation
        # To pass without human intervention, overall score must be >= threshold AND essential fields (sender, topic) must be valid
        has_essential_fields = bool(detected_sender and detected_topic)
        passed_threshold = (total_score >= self.DEFAULT_THRESHOLD) and has_essential_fields

        parsing_status = "PASSED_THRESHOLD" if passed_threshold else "REQUIRES_HUMAN_REVIEW"

        snippet = raw_text[:300] if raw_text else None

        return ParsedCandidateFields(
            sender=detected_sender or "Unidentified Sender",
            sender_email=detected_email or "unknown@domain.com",
            sender_contact_number=detected_phone,
            darta_date=detected_date_ad or date.today().isoformat(),
            darta_date_bs=detected_date_bs or "2081-05-09",
            financial_year=fy_id,
            topic=detected_topic or "Official Correspondence Letter",
            suggested_department_id=suggested_dept_id,
            suggested_department_name=suggested_dept_name,
            suggested_officer_id=suggested_officer_id,
            suggested_officer_name=suggested_officer_name,
            confidence_score=total_score,
            parsing_status=parsing_status,
            threshold=self.DEFAULT_THRESHOLD,
            field_confidences=field_confidences,
            extracted_text_snippet=snippet,
            detected_language="ne/en"
        )


class LLMDocumentParser(BaseDocumentParser):
    """
    Extensible LLM Parser stub.
    When custom LLM context guidelines and prompt schemas are provided in the future,
    this class can be invoked directly with zero architectural changes.
    """
    def __init__(self, model_name: str = "gemini-flash"):
        self.model_name = model_name

    def parse_text(self, text: str, db: Optional[Session] = None, metadata: Optional[Dict[str, Any]] = None) -> ParsedCandidateFields:
        # Fallback to Heuristic parser until LLM context credentials/prompt guidelines are configured
        fallback_parser = HeuristicOCRDocumentParser()
        return fallback_parser.parse_text(text, db, metadata)


class DocumentParsingService:
    """
    Unified entry point for document parsing across all ingestion vectors:
    - Canon / Hardware Scanners
    - Raw PDF / Image Uploads
    - Inbound SMTP Emails
    """
    def __init__(self, db: Optional[Session] = None, parser: Optional[BaseDocumentParser] = None):
        self.db = db
        self.parser = parser or HeuristicOCRDocumentParser()

    def parse_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> ParsedCandidateFields:
        """
        Extract OCR text from file and parse structured candidate fields.
        """
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found at: {file_path}")

        # Extract text via OCR
        raw_text = OCRService.extract_text(file_path)
        return self.parser.parse_text(text=raw_text, db=self.db, metadata=metadata)

    def parse_raw_text(self, raw_text: str, metadata: Optional[Dict[str, Any]] = None) -> ParsedCandidateFields:
        """
        Parse structured candidate fields directly from provided text.
        """
        return self.parser.parse_text(text=raw_text, db=self.db, metadata=metadata)
