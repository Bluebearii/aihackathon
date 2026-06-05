import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

# Drop existing to apply new schema
if os.path.exists("carepoint.db"):
    os.remove("carepoint.db")

import models
from database import SessionLocal, engine
from datetime import date

models.Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    if not db.query(models.User).first():
        hashed_pw = get_password_hash("password123")
        patient = models.User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password_hash=hashed_pw,
            phone="555-0100",
            address="123 Main St",
            date_of_birth=date(1980, 5, 15),
            role="patient"
        )
        admin = models.User(
            first_name="Sarah",
            last_name="Staff",
            email="sarah@carepoint.com",
            password_hash=hashed_pw,
            phone="555-0200",
            address="456 Clinic Way",
            date_of_birth=date(1985, 8, 22),
            role="admin"
        )
        db.add(patient)
        db.add(admin)
        
        default_dash = models.ExternalDashboard(
            name="Main Analytics",
            url="http://localhost:8501",
            description="The primary internal data visualization dashboard."
        )
        db.add(default_dash)
        
        db.commit()
        print("Database initialized with new auth schema.")
    else:
        print("Database already initialized.")
    db.close()

if __name__ == "__main__":
    init_db()
