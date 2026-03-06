from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
import uuid
from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.core.config import settings
from app.models.database import Order, OrderStatusEnum, User, Template
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
router = APIRouter()


@router.post("/", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Create a new order.
    """
    # 验证模板是否存在
    template = db.query(Template).filter(Template.id == order_in.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 验证用户是否存在
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    template_price = float(template.price) if hasattr(template, 'price') and template.price else settings.DEFAULT_TEMPLATE_PRICE
    current_balance = float(user.credits or 0)

    if current_balance < template_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # 扣减余额并创建订单
    user.credits = current_balance - template_price

    order_id = str(uuid.uuid4())
    order = Order(
        id=order_id,
        user_id=current_user_id,
        template_id=order_in.template_id,
        status=OrderStatusEnum.COMPLETED,
        amount=template_price,
        credits_consumed=template_price,
        credits_purchased=0,
        platform="web",
        result_image_url=template.display_image_urls[0] if template.display_image_urls else settings.DEFAULT_RESULT_IMAGE_PLACEHOLDER
    )

    # 更新模板使用次数
    template.usage_count = (template.usage_count or 0) + 1

    db.add(order)
    db.commit()
    db.refresh(order)
    db.refresh(user)
    db.refresh(template)

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
        result_image_url=getattr(order, 'result_image_url', None),
        created_at=order.created_at,
        updated_at=order.updated_at
    )