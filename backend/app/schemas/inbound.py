from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class FieldConfidence(BaseModel):
    value: Optional[Any] = None
    confidence: float = 0.0  # 0.0 to 1.0
    is_high_confidence: bool = False
    source: str = "auto_extracted"  # auto_extracted, rule_matched, fallback

class ParsedCandidateFields(BaseModel):
    sender: Optional[str] = None
    sender_email: Optional[str] = None
    sender_contact_number: Optional[str] = None
    darta_date: Optional[str] = None
    darta_date_bs: Optional[str] = None
    financial_year: Optional[int] = None
    topic: Optional[str] = None
    suggested_department_id: Optional[int] = None
    suggested_department_name: Optional[str] = None
    suggested_officer_id: Optional[int] = None
    suggested_officer_name: Optional[str] = None
    confidence_score: float = 0.0
    parsing_status: str = "REQUIRES_HUMAN_REVIEW"  # PASSED_THRESHOLD, REQUIRES_HUMAN_REVIEW, FAILED
    threshold: float = 0.80  # Default high confidence threshold (80%)
    field_confidences: Dict[str, FieldConfidence] = Field(default_factory=dict)
    extracted_text_snippet: Optional[str] = None
    detected_language: Optional[str] = "en/ne"

class InboundDocumentResponse(BaseModel):
    id: int
    source: str
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    subject: Optional[str] = None
    file_name: str
    confidence_score: Optional[float] = 0.0
    parsing_status: str
    status: str
    parsed_data: Optional[ParsedCandidateFields] = None
    extracted_ocr_text: Optional[str] = None
    target_office_id: Optional[int] = None
    target_department_id: Optional[int] = None
    assigned_to_user_id: Optional[int] = None
    converted_darta_id: Optional[int] = None
    converted_chalan_id: Optional[int] = None
    received_at: datetime

    model_config = {"from_attributes": True}

class InboundDocumentFilter(BaseModel):
    status: Optional[str] = None
    source: Optional[str] = None
    parsing_status: Optional[str] = None
    search: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class ConvertInboundToDarta(BaseModel):
    sender: str
    sender_email: str
    sender_contact_number: Optional[str] = None
    darta_date: date
    darta_date_bs: Optional[str] = None
    financial_year: int
    topic: str
    receiver_department: Optional[int] = None
    receiver_officer: Optional[int] = None

class SimulateEmailRequest(BaseModel):
    sender_email: str = "contact@ministry.gov.np"
    sender_name: str = "Ministry of Communications & IT"
    subject: str = "Regarding Telecommunication Infrastructure Expansion 2081/82"
    body: Optional[str] = "Please find attached the official directive letter regarding optical fiber expansion."
    file_content_base64: Optional[str] = None
    file_name: Optional[str] = "official_directive_letter.pdf"
    target_office_id: Optional[int] = None

class SMTPScannerStatusResponse(BaseModel):
    running: bool
    host: str
    port: int
    uptime_seconds: float
    messages_processed: int
    last_message_at: Optional[str] = None
    last_sender: Optional[str] = None
    last_subject: Optional[str] = None
    last_error: Optional[str] = None
    max_message_mb: int
    allowed_domains: List[str]

class SMTPTestEmailRequest(BaseModel):
    sender_email: Optional[str] = "scanner.canon@ntc.net.np"
    sender_name: Optional[str] = "Canon imageRUNNER 2520 (Branch Scanner)"
    subject: Optional[str] = "Scanned Official Memorandum - Broadband Expansion 2081"
    file_name: Optional[str] = "canon_scan_doc_2081.pdf"

class SMTPToggleRequest(BaseModel):
    enable: bool
