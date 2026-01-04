"""Order API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
import uuid
from datetime import datetime
from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_user_id
from app.models.database import Order, User, Template
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Create a new order.
    """
    # 使用同步会话以兼容现有代码
    db = SyncSessionLocal()
    try:
        # 验证模板是否存在
        template = db.query(Template).filter(Template.id == order_in.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # 获取用户
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 检查用户余额
        price = float(template.price) if hasattr(template, 'price') and template.price else 9.9
        if user.credits < price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # 扣除用户余额
        user.credits -= int(price)
        
        # 创建订单
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            user_id=current_user_id,
            template_id=order_in.template_id,
            status="PROCESSING",  # 订单状态
            amount=price,
            credits_consumed=price,
            credits_purchased=0,
            platform="web"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # TODO: 在实际生产环境中，应该将订单发送到消息队列（如Celery）进行异步处理
        # 这里简化处理，模拟订单立即完成
        # import asyncio
        # await asyncio.sleep(1)  # 使用异步sleep而非同步
        order.status = "COMPLETED"
        order.result_image_url = template.display_image_urls[0] if template.display_image_urls else "https://images.unsplash.com/photo-1543128639-4cb7e25b4e3d?w=800&q=80"
        db.commit()
        
        # 返回订单信息
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            template_id=order.template_id,
            status=order.status,
            amount=float(order.amount),
            credits_consumed=float(order.credits_consumed),
            result_image_url=order.result_image_url,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
    finally:
        db.close()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str
) -> Any:
    """
    Get order by ID.
    """
    # 使用同步会话以兼容现有代码
    db = SyncSessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # 获取关联的模板信息
        template = db.query(Template).filter(Template.id == order.template_id).first()
        
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            template_id=order.template_id,
            status=order.status,
            amount=float(order.amount),
            credits_consumed=float(order.credits_consumed),
            result_image_url=order.result_image_url if order.result_image_url else f"https://images.unsplash.com/photo-1543128639-4cb7e25b4e3d?w=800&q=80",
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    finally:
        db.close()