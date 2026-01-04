"""Authentication API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from datetime import timedelta
from pydantic import BaseModel, EmailStr

from app.core.database import SyncSessionLocal
from app.core.dependencies import create_access_token
from app.core.security import get_password_hash, verify_password
from app.models.database import User
from app.core.config import settings
import uuid

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest
) -> Any:
    """
    User login endpoint
    """
    db = SyncSessionLocal()
    try:
        # 查找用户
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # 验证密码
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "email": user.email,
                "credits": user.credits,
                "roles": user.roles,
                "face_image_url": user.face_image_url,
                "gender": user.gender
            }
        )
    finally:
        db.close()


@router.post("/register", response_model=TokenResponse)
def register(
    register_data: RegisterRequest
) -> Any:
    """
    User registration endpoint
    """
    db = SyncSessionLocal()
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.email == register_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 创建新用户
        user = User(
            id=str(uuid.uuid4()),
            email=register_data.email,
            password_hash=get_password_hash(register_data.password),
            credits=100,  # 新用户赠送100积分
            roles=["user"]
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "email": user.email,
                "credits": user.credits,
                "roles": user.roles,
                "face_image_url": user.face_image_url,
                "gender": user.gender
            }
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )
    finally:
        db.close()
