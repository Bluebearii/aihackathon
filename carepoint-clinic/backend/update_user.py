from database import SessionLocal
import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

def update_user():
    db = SessionLocal()
    # Find the admin user (we know it had role admin)
    admin = db.query(models.User).filter(models.User.role == "admin").first()
    if admin:
        admin.email = "anthony_tran@careflowai.com"
        admin.first_name = "Anthony"
        admin.last_name = "Tran"
        admin.password_hash = get_password_hash("password123")
        db.commit()
        print("Admin user updated successfully.")
    else:
        print("Admin user not found.")
    db.close()

if __name__ == "__main__":
    update_user()
