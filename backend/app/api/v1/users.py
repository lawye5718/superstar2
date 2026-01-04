"""User API routes"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
import shutil
import os
import uuid

from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_user_id
from app.models.database import User
from app.schemas.user import UserResponse
import asyncio

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Get current user.
    """
    # 使用同步会话以兼容现有代码
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            # 自动注册一个测试用户 (方便 MVP 演示)
            user = User(
                id=current_user_id,
                email="demo@example.com",
                password_hash="dummy_hash",
                credits=100,
                roles=["user"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


@router.post("/face", response_model=dict)
async def upload_face(
    file: UploadFile = File(...),  # 接收文件
    gender: str = Form(...),       # 接收表单字段
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Upload user face image.
    """
    # 1. 验证文件
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 2. 确保上传目录存在
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 3. 生成文件名并保存
    # 注意：生产环境这里应上传到 S3/OSS
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = f"{upload_dir}/{new_filename}"
    
    try:
        with open(file_location, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
        
    # 4. 生成访问 URL
    # 假设后端运行在 localhost:8000
    file_url = f"http://localhost:8000/{file_location}"
    
    # 5. 更新数据库
    # 使用同步会话以兼容现有代码
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.face_image_url = file_url
        user.gender = gender
        db.commit()
        
        return {"status": "success", "url": file_url}
    finally:
        db.close()