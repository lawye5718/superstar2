"""User API routes"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
import aiofiles
import os
import uuid

from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_user_id, get_db
from app.core.security import get_password_hash
from app.models.database import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
import asyncio

router = APIRouter()


# --- 新增：注册接口 ---
@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")
    
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        username=user_in.username or user_in.email.split("@")[0],
        credits=100.0, # 注册赠送 100 积分
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
def read_user_me(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- 新增：模拟充值接口 (测试用) ---
@router.post("/topup", response_model=UserResponse)
def top_up_balance(
    amount: float = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Add balance to user account (Mock Payment).
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.credits += amount
    db.commit()
    db.refresh(user)
    return user

@router.post("/face", response_model=dict)
async def upload_face(
    request: Request,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    gender: str = Form(...),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, new_filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/{file_path}"
    
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.face_image_url = file_url
    user.gender = gender
    db.commit()
    
    return {"status": "success", "url": file_url}