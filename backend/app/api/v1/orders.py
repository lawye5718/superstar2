from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
import uuid
from datetime import datetime
from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_user_id
from app.core.config import settings
from app.models.database import Order, User, Template
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate

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
        
        # 验证用户是否存在
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 创建订单
        order_id = str(uuid.uuid4())
        template_price = float(template.price) if hasattr(template, 'price') and template.price else settings.DEFAULT_TEMPLATE_PRICE
        
        order = Order(
            id=order_id,
            user_id=current_user_id,
            template_id=order_in.template_id,
            status="PENDING",  # 订单状态
            amount=template_price,  # 使用模板价格
            credits_consumed=template_price,  # 消耗积分
            credits_purchased=0,  # 积分套餐订单才有这个值
            platform="web"  # 默认平台
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # 返回订单信息
        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            template_id=str(order.template_id) if order.template_id else None,
            status=order.status.value if hasattr(order.status, 'value') else str(order.status),
            amount=float(order.amount),
            credits_consumed=float(order.credits_consumed) if order.credits_consumed else None,
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
    order_id: str,
    current_user_id: str = Depends(get_current_user_id)
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
        
        # 验证订单属于当前用户
        if str(order.user_id) != str(current_user_id):
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
        
        # 获取关联的模板信息
        template = db.query(Template).filter(Template.id == order.template_id).first()
        
        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            template_id=str(order.template_id) if order.template_id else None,
            status=order.status.value if hasattr(order.status, 'value') else str(order.status),
            amount=float(order.amount),
            credits_consumed=float(order.credits_consumed) if order.credits_consumed else None,
            result_image_url=getattr(order, 'result_image_url', None),  # 返回实际URL或None
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    finally:
        db.close()