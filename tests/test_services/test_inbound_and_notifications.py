import pytest
from datetime import date
from backend.app.services.parsing_service import DocumentParsingService, HeuristicOCRDocumentParser
from backend.app.services.inbound_service import InboundService
from backend.app.services.notification_service import NotificationService
from backend.app.schemas.inbound import ConvertInboundToDarta

def test_heuristic_parsing_with_high_threshold(db_session, test_department, test_officer, test_financial_year):
    sample_text = """
    Government of Nepal
    Ministry of Communications and Information Technology
    Singha Durbar, Kathmandu

    From: Ministry of Communications
    Email: info@mocit.gov.np
    Tel: +977-1-4211555

    Date: 2026-08-25
    Miti: 2081-05-09

    Subject: Approval for Optical Fiber Expansion Project across Province 3

    To: IT Department, Nepal Telecom Central Office.

    Please proceed with the immediate implementation of the project.
    """

    parsing_service = DocumentParsingService(db=db_session)
    result = parsing_service.parse_raw_text(sample_text)

    assert result.sender is not None
    assert "Ministry of Communications" in result.sender
    assert result.sender_email == "info@mocit.gov.np"
    assert result.topic is not None
    assert "Optical Fiber Expansion" in result.topic
    assert result.suggested_department_id == test_department.id
    assert result.confidence_score >= 0.80
    assert result.parsing_status == "PASSED_THRESHOLD"


def test_heuristic_parsing_low_confidence_requires_review(db_session):
    low_quality_text = "Some random scanned blur without clear headers or email."

    parsing_service = DocumentParsingService(db=db_session)
    result = parsing_service.parse_raw_text(low_quality_text)

    assert result.confidence_score < 0.80
    assert result.parsing_status == "REQUIRES_HUMAN_REVIEW"


def test_inbound_document_flow_and_notification(db_session, test_admin_user, test_office, test_financial_year):
    inbound_service = InboundService(db_session)
    notif_service = NotificationService(db_session)

    mock_pdf_bytes = b"%PDF-1.4 Mock document content for testing inbound reception"
    
    # Receive inbound document
    doc = inbound_service.receive_inbound_document(
        file_bytes=mock_pdf_bytes,
        file_name="incoming_sample.pdf",
        source="SMTP_EMAIL",
        sender_email="test.sender@domain.np",
        sender_name="Ministry Test Office",
        subject="Regarding System Upgrades",
        target_office_id=test_office.id,
        auto_parse=True
    )

    assert doc.id is not None
    assert doc.status == "PENDING_REVIEW"
    assert doc.source == "SMTP_EMAIL"

    # Verify notification created
    unread_count = notif_service.get_unread_count(test_admin_user)
    assert unread_count >= 1

    notifs = notif_service.get_user_notifications(test_admin_user, unread_only=True)
    assert len(notifs) >= 1
    assert notifs[0].inbound_doc_id == doc.id

    # Convert to Darta
    darta_payload = ConvertInboundToDarta(
        sender="Ministry Test Office",
        sender_email="test.sender@domain.np",
        sender_contact_number="9841234567",
        darta_date=date(2026, 8, 25),
        darta_date_bs="2081-05-09",
        financial_year=test_financial_year.id,
        topic="Regarding System Upgrades"
    )

    darta = inbound_service.convert_to_darta(doc.id, darta_payload, test_admin_user)
    assert darta.id is not None
    assert darta.darta_id > 0
    assert darta.topic == "Regarding System Upgrades"

    # Verify inbound document marked converted
    refreshed_doc = inbound_service.inbound_repo.get_by_id(doc.id)
    assert refreshed_doc.status == "CONVERTED_TO_DARTA"
    assert refreshed_doc.converted_darta_id == darta.id
