"""User API routes"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Body
from sqlalchemy.orm import Session
from typing import Any
import shutil
import os
import uuid
import aiofiles

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.core.security import get_password_hash
from app.models.database import User
from app.schemas.user import UserCreate, UserResponse
from app.core.file_validator import validate_uploaded_file # ✅ 导入校验器

router = APIRouter()

# --- 新增：注册接口 ---
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
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- 新增：模拟充值接口 (测试用) ---
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
    # 1. 读取文件内容
    content = await file.read()
    
    try:
        # ✅ 修复：进行完整的文件安全验证
        file_extension = validate_uploaded_file(file.filename or "", content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, new_filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # ✅ 修复：使用配置中的域名，而非 request.base_url (防止反向代理问题)
    from app.core.config import settings
    file_url = f"{settings.DOMAIN}/{upload_dir}/{new_filename}"
    
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.face_image_url = file_url
    user.gender = gender
    db.commit()
    
    return {"status": "success", "url": file_url}
