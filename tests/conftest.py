import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.base import Base
from backend.app.db.models import (
    Users, Offices, Departments, Officers, FinancialYear
)
from backend.app.enums import USER_TYPE
from backend.app.core.security import hash_password

from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_office(db_session):
    office = Offices(name="Kathmandu Office", location="Kathmandu")
    db_session.add(office)
    db_session.commit()
    db_session.refresh(office)
    return office

@pytest.fixture
def test_department(db_session, test_office):
    dept = Departments(name="IT Department")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept

@pytest.fixture
def test_officer(db_session, test_department, test_office):
    officer = Officers(name="John Officer", department=test_department.id, office=test_office.id)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    return officer

@pytest.fixture
def test_financial_year(db_session):
    fy = FinancialYear(financial_year="2080/81")
    db_session.add(fy)
    db_session.commit()
    db_session.refresh(fy)
    return fy

@pytest.fixture
def test_admin_user(db_session, test_office):
    user = Users(
        full_name="Admin Test",
        email="admin.test@ntc.net.np",
        password=hash_password("Secret123!"),
        user_type=USER_TYPE.SYSTEM_ADMIN,
        user_office=test_office.id,
        is_disabled=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_staff_user(db_session, test_office):
    user = Users(
        full_name="Staff Test",
        email="staff.test@ntc.net.np",
        password=hash_password("Secret123!"),
        user_type=USER_TYPE.STAFF,
        user_office=test_office.id,
        is_disabled=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def client(db_session):
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db.base import get_db

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


