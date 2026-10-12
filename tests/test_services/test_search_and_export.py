import pytest
from datetime import date
from backend.app.services.document_workflow import DocumentWorkflowService
from backend.app.services.search_service import SearchService
from backend.app.services.export_service import ExportService
from backend.app.schemas import CreateDarta, CreateChalan

def test_search_and_export_services(db_session, test_staff_user, test_office, test_financial_year, tmp_path):
    dummy_file = tmp_path / "search_export_doc.pdf"
    dummy_file.write_text("Searchable document text content")

    workflow = DocumentWorkflowService(db_session)
    search_service = SearchService(db_session)
    export_service = ExportService(db_session)

    # Create Darta
    darta_in = CreateDarta(
        sender="Ministry of IT",
        sender_email="mit@gov.np",
        darta_date=date(2023, 10, 1),
        topic="5G Expansion Proposal",
        receiver_office=test_office.id,
        financial_year=test_financial_year.id
    )
    workflow.create_darta(test_staff_user, darta_in, str(dummy_file))

    # Create Chalan
    chalan_in = CreateChalan(
        receiver="Nepal Telecom Board",
        receiver_email="board@ntc.net.np",
        sender_email="staff@ntc.net.np",
        chalan_date=date(2023, 10, 2),
        topic="5G Approval Letter",
        sender_office=test_office.id
    )
    workflow.create_chalan(test_staff_user, chalan_in, str(dummy_file))

    # Test Advanced Search
    darta_results = search_service.advanced_search_darta(
        user=test_staff_user,
        query_text="5G Expansion",
        receiver_office=test_office.id
    )
    assert len(darta_results) == 1
    assert darta_results[0].topic == "5G Expansion Proposal"

    chalan_results = search_service.advanced_search_chalan(
        user=test_staff_user,
        query_text="Approval",
        sender_office=test_office.id
    )
    assert len(chalan_results) == 1
    assert chalan_results[0].receiver == "Nepal Telecom Board"

    # Test CSV Export
    darta_csv = export_service.export_darta_register_csv(test_staff_user, receiver_office=test_office.id)
    assert "System ID" in darta_csv
    assert "Ministry of IT" in darta_csv

    chalan_csv = export_service.export_chalan_register_csv(test_staff_user, sender_office=test_office.id)
    assert "System ID" in chalan_csv
    assert "Nepal Telecom Board" in chalan_csv
