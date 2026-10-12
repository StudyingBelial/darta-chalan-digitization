import pytest
from datetime import date
from backend.app.services.document_workflow import DocumentWorkflowService
from backend.app.services.forwarding_service import ForwardingService
from backend.app.schemas import CreateDarta
from backend.app.enums import DOCUMENT_STATUS

def test_forward_darta_document(db_session, test_staff_user, test_office, test_department, test_officer, test_financial_year, tmp_path):
    dummy_file = tmp_path / "forward_doc.pdf"
    dummy_file.write_text("Forward test")

    workflow_service = DocumentWorkflowService(db_session)
    forwarding_service = ForwardingService(db_session)

    darta_in = CreateDarta(
        sender="Department of Finance",
        sender_email="finance@gov.np",
        darta_date=date(2023, 9, 1),
        topic="Budget Request",
        receiver_office=test_office.id,
        financial_year=test_financial_year.id
    )

    darta = workflow_service.create_darta(
        user=test_staff_user,
        darta_data=darta_in,
        file_path=str(dummy_file)
    )

    forward_record = forwarding_service.forward_document(
        user=test_staff_user,
        document_type="DARTA",
        document_id=darta.id,
        target_office=test_office.id,
        target_department=test_department.id,
        target_officer=test_officer.id,
        remarks="Please take necessary action"
    )

    assert forward_record.id is not None
    assert forward_record.document_type == "DARTA"
    assert forward_record.document_id == darta.id
    assert forward_record.forwarded_by_user == test_staff_user.id
    assert forward_record.remarks == "Please take necessary action"

    history = forwarding_service.get_forwarding_history(test_staff_user, "DARTA", darta.id)
    assert len(history) == 1
    assert history[0].id == forward_record.id
