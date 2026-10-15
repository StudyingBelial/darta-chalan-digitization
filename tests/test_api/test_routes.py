import os
from io import BytesIO
from backend.app.core.security import create_access_token

def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_auth_login_success(client, test_admin_user):
    payload = {
        "email": test_admin_user.email,
        "password": "Secret123!",
        "user_type": "SYSTEM_ADMIN"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_admin_user.email

def test_auth_login_failure(client, test_admin_user):
    payload = {
        "email": test_admin_user.email,
        "password": "WrongPassword123",
        "user_type": "SYSTEM_ADMIN"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

def test_system_stats(client, test_admin_user):
    token = create_access_token({"sub": str(test_admin_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/system/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "statistics" in data
    assert data["statistics"]["active_user_accounts"] >= 1

def test_create_darta_route(client, test_admin_user, test_financial_year, tmp_path):
    token = create_access_token({"sub": str(test_admin_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    file_content = b"Sample Darta Content for API Test"
    files = {
        "file": ("test_doc.pdf", BytesIO(file_content), "application/pdf")
    }
    params = {
        "sender": "Ministry of Communication",
        "sender_email": "moc@gov.np",
        "darta_date": "2024-07-24",
        "financial_year": test_financial_year.id,
        "topic": "Official Telecom Policy Review"
    }

    response = client.post("/api/v1/darta", data=params, files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["sender"] == "Ministry of Communication"
    assert data["topic"] == "Official Telecom Policy Review"
    assert data["darta_id"] > 0

def test_export_darta_csv_route(client, test_admin_user):
    token = create_access_token({"sub": str(test_admin_user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/export/darta", headers=headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Darta No" in response.text
