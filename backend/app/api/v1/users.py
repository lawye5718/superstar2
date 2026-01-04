"""User API routes"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any, List
from pydantic import BaseModel
import aiofiles
import os
import uuid

from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_user_id
from app.models.database import User, Order
from app.schemas.user import UserResponse
from app.schemas.order import OrderResponse
import asyncio

router = APIRouter()


class TopUpRequest(BaseModel):
    amount: int  # 充值金额，对应积分


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


@router.post("/top-up", response_model=UserResponse)
def top_up_balance(
    top_up_data: TopUpRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Top up user balance/credits
    """
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 增加用户余额
        user.credits += top_up_data.amount
        db.commit()
        db.refresh(user)
        
        return user
    finally:
        db.close()


@router.get("/orders", response_model=List[OrderResponse])
def get_user_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Get user's order history
    """
    db = SyncSessionLocal()
    try:
        orders = db.query(Order).filter(
            Order.user_id == current_user_id
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for order in orders:
            result.append(OrderResponse(
                id=order.id,
                user_id=order.user_id,
                template_id=order.template_id,
                status=order.status,
                amount=float(order.amount),
                credits_consumed=float(order.credits_consumed),
                result_image_url=order.result_image_url,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))
        
        return result
    finally:
        db.close()


@router.post("/face", response_model=dict)
async def upload_face(
    request: Request,
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
    file_path = os.path.join(upload_dir, new_filename)
    
    # 4. 异步写入文件 (解决阻塞问题)
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            # 分块读取，防止内存溢出
            while content := await file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
        
    # 5. 动态生成 URL (解决 localhost 硬编码问题)
    # request.base_url 会自动根据访问的域名/IP变化
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/{file_path}"
    
    # 6. 更新数据库
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