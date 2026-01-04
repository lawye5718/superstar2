"""Create admin user for testing"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings
from app.models.database import User
from app.core.security import get_password_hash
import uuid

settings = get_settings()

# 使用同步引擎
engine = create_engine(settings.DATABASE_SYNC_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_admin_user():
    """Create admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            # Create admin user
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                credits=1000,
                roles=["user", "admin"]
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully!")
            print("Email: admin@example.com")
            print("Password: admin123")
        else:
            print("Admin user already exists!")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
