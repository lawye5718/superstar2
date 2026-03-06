"""User API routes"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Body
from sqlalchemy.orm import Session
from typing import Any
import os
import uuid
import aiofiles

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.core.security import get_password_hash
from app.models.database import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.api.v1.helpers import normalize_balance_payload

router = APIRouter()


# --- 注册接口 ---
@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_sync_db)
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
        credits=100.0,  # 注册赠送 100 积分
        is_active=True,
        roles=["user"],
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Get current user.
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """Update basic profile for current user."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = normalize_balance_payload(user_in.model_dump(exclude_unset=True))

    for field, value in update_data.items():
        if hasattr(user, field) and field not in ("balance", "is_superuser", "is_active", "roles"):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# --- 模拟充值接口 (测试用) ---
@router.post("/topup", response_model=UserResponse)
def top_up_balance(
    amount: float = Body(..., embed=True),
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Add balance to user account (Mock Payment).
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Top-up amount must be positive")

    current_balance = float(user.credits or 0)
    user.credits = current_balance + amount
    db.commit()
    db.refresh(user)
    return user


@router.post("/face", response_model=dict)
async def upload_face(
    request: Request,
    db: Session = Depends(get_sync_db),
    file: UploadFile = File(...),
    gender: str = Form(...),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Upload user face image.
    """
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
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
        
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/{upload_dir}/{new_filename}"
    
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.face_image_url = file_url
    user.gender = gender
    db.commit()
    
    return {"status": "success", "url": file_url}