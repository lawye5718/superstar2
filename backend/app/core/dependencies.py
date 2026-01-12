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


def get_current_user(db: Session = Depends(get_sync_db), credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    获取当前用户
    """
    token = credentials.credentials
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    # 🛑【严重修复】：删除了此处自动创建用户的代码
    # 原有的自动创建逻辑会导致任意伪造的 token 都能注册并在系统中扣款，极度危险。
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


def get_current_active_user(db: Session = Depends(get_sync_db), credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    获取当前活跃用户 (alias for get_current_user for backward compatibility)
    Note: get_current_user already checks is_active status
    """
    return get_current_user(db=db, credentials=credentials)
