from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
import uuid
from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.core.config import settings
from app.models.database import Order, OrderStatusEnum, User, Template
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import OrderService # ✅ 导入服务
router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Create a new order (Transactional).
    """
    service = OrderService(db)
    # ✅ 修复：使用事务服务创建订单
    order = service.create_order_with_transaction(current_user_id, order_in.template_id)

    return OrderResponse(
        id=str(order.id),
        user_id=str(order.user_id),
        template_id=str(order.template_id) if order.template_id else None,
        status=order.status.value if hasattr(order.status, 'value') else str(order.status),
        amount=float(order.amount),
        credits_consumed=float(order.credits_consumed) if order.credits_consumed else None,
        result_image_url=order.result_image_url,
        created_at=order.created_at,
        updated_at=order.updated_at
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Any:
    """
    Get order by ID.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 验证订单属于当前用户
    if str(order.user_id) != str(current_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
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


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """List current user's orders"""
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            template_id=str(order.template_id) if order.template_id else None,
            status=order.status.value if hasattr(order.status, 'value') else str(order.status),
            amount=float(order.amount),
            credits_consumed=float(order.credits_consumed) if order.credits_consumed else None,
            result_image_url=getattr(order, 'result_image_url', None),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        for order in orders
    ]
