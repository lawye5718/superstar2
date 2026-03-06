"""Dependency management for FastAPI"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator
import uuid

from .database import get_db, get_sync_db
from app.models.database import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    从JWT token中解析用户ID
    """
    token = credentials.credentials
    return verify_token(token)


def get_current_user(db: Session = Depends(get_sync_db)):
    """
    获取当前用户
    """
    user_id = get_current_user_id()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # 自动注册一个测试用户 (方便 MVP 演示)
        user = User(
            id=user_id,
            email="demo@example.com",
            password_hash=get_password_hash("default_password"),
            credits=100,
            roles=["user"],
            username="demo",
            is_superuser=False,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_active_superuser(
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> User:
    """Get current user and verify they are a superuser."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not getattr(user, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user