from backend.app.db.base import Base, engine, SessionLocal
from backend.app.db.models import (
    Users, Offices, Departments, Officers, FinancialYear
)
from backend.app.enums import USER_TYPE
from backend.app.core.security import hash_password
from backend.app.services.date_service import DateService
from backend.app.core.logger import logger

def seed_database():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Financial Year
        current_fy_str = DateService.get_nepali_fiscal_year()
        fy = db.query(FinancialYear).filter(FinancialYear.financial_year == current_fy_str).first()
        if not fy:
            fy = FinancialYear(financial_year=current_fy_str)
            db.add(fy)
            db.commit()
            db.refresh(fy)
            logger.info(f"Seeded Financial Year: {current_fy_str}")

        # 2. Seed Primary Office
        office = db.query(Offices).filter(Offices.name == "NTC Central Office").first()
        if not office:
            office = Offices(
                name="NTC Central Office",
                location="Bhadrakali Plaza, Kathmandu"
            )
            db.add(office)
            db.commit()
            db.refresh(office)
            logger.info("Seeded Office: NTC Central Office")

        # 3. Seed Primary Department
        dept = db.query(Departments).filter(Departments.name == "Administration Department").first()
        if not dept:
            dept = Departments(name="Administration Department")
            db.add(dept)
            db.commit()
            db.refresh(dept)
            logger.info("Seeded Department: Administration Department")

        # 4. Seed Primary Officer
        officer = db.query(Officers).filter(Officers.name == "Chief Administrative Officer").first()
        if not officer:
            officer = Officers(
                name="Chief Administrative Officer",
                department=dept.id,
                office=office.id
            )
            db.add(officer)
            db.commit()
            db.refresh(officer)
            logger.info("Seeded Officer: Chief Administrative Officer")

        # 5. Seed System Admin User
        admin_email = "admin@ntc.net.np"
        admin_user = db.query(Users).filter(Users.email == admin_email).first()
        if not admin_user:
            admin_user = Users(
                full_name="System Admin",
                email=admin_email,
                password=hash_password("Admin@123456"),
                user_type=USER_TYPE.SYSTEM_ADMIN,
                user_office=office.id,
                is_disabled=False
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Seeded System Admin: {admin_email}")

        logger.info("Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

# Alias for compatibility with external runners
seed_initial_data = seed_database
