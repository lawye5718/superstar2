"""Order API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
import uuid
from datetime import datetime
from app.core.database import SyncSessionLocal
from app.models.database import Order, User, Template
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate
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
        
        # 创建订单
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            user_id="test-user-uuid-001",  # 临时硬编码，实际应从认证信息中获取
            template_id=order_in.template_id,
            status="PENDING",  # 订单状态
            amount=template.price if hasattr(template, 'price') else 9.9,  # 使用模板价格
            credits_consumed=template.price if hasattr(template, 'price') else 9.9  # 消耗积分
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 返回订单信息
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            template_id=order.template_id,
            status=order.status,
            amount=order.amount,
            credits_consumed=order.credits_consumed,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
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
            amount=order.amount,
            credits_consumed=order.credits_consumed,
            result_image_url=getattr(order, 'result_image_url', f"https://images.unsplash.com/photo-1543128639-4cb7e25b4e3d?w=800&q=80"),  # 临时结果图片
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    finally:
        db.close()