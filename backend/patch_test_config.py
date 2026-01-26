"""Patch test configuration to handle UUID in SQLite"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_sync_db
from app.models.database import User, get_uuid_type, generate_uuid
from app.core.security import get_password_hash


# Override the DATABASE_URL for tests to ensure SQLite compatibility
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///./test.db'


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    # Re-import after setting env vars to ensure proper UUID handling
    from app.models.database import get_uuid_type
    
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_sync_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("testpassword123A"),
        credits=100.0,
        is_active=True,
        is_superuser=False,
        roles=["user"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db):
    """Create an admin user"""
    user = User(
        email="admin@example.com",
        username="admin",
        password_hash=get_password_hash("adminpassword123A"),
        credits=999999.0,
        is_active=True,
        is_superuser=True,
        roles=["user", "admin"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


if __name__ == "__main__":
    print("Test config patch ready.")
