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
from app.core.image_processor import image_processor_manager
from app.services.user_service import UserService # ✅ 引入服务层

router = APIRouter()

# --- 新增：注册接口 ---
@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_sync_db)
) -> Any:
    """
    Create new user with strict validation.
    """
    service = UserService(db)
    return service.create_user(user_in)

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
    Mock Top-up API.
    """
    service = UserService(db)
    return service.top_up_balance(current_user_id, amount)

@router.post("/face", response_model=dict)
async def upload_face(
    request: Request,
    db: Session = Depends(get_sync_db),
    file: UploadFile = File(...),
    gender: str = Form(...),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Upload user face image to COS.
    """
    # 1. 异步读取文件 (IO Bound)
    content = await file.read()
    
    # 2. 校验文件 (CPU Bound)
    try:
        validate_uploaded_file(file.filename or "", content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 3. 上传到 COS (Network IO Bound)
    try:
        result = await image_processor_manager.upload_example_image(content, file.filename)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Upload failed"))
        
        file_url = result["url"]
        
        # 4. 更新数据库 (Sync IO)
        # ✅ 使用 Service 更新，保持事务一致性
        service = UserService(db)
        service.update_face_info(current_user_id, file_url, gender)
        
        return {"status": "success", "url": file_url, "cos_key": result.get("cos_key")}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
