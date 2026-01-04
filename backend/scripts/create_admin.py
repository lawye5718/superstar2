"""Create admin user for testing"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings
from app.models.database import User
from app.core.security import get_password_hash
import uuid
import secrets
import string

settings = get_settings()

# 使用同步引擎
engine = create_engine(settings.DATABASE_SYNC_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def create_admin_user(email="admin@example.com", password=None):
    """Create admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == email).first()
        if not admin:
            # Generate password if not provided
            if password is None:
                password = generate_password()
                print(f"Generated password: {password}")
            
            # Create admin user
            admin = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=get_password_hash(password),
                credits=1000,
                roles=["user", "admin"]
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully!")
            print(f"Email: {email}")
            if password != generate_password():  # If password was provided
                print(f"Password: {password}")
        else:
            print("Admin user already exists!")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    # Allow password to be passed as command line argument
    # Usage: python create_admin.py [email] [password]
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@example.com"
    password = sys.argv[2] if len(sys.argv) > 2 else None
    create_admin_user(email, password)
