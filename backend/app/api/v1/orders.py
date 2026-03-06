from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
import uuid
from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.core.config import settings
from app.models.database import Order, OrderStatusEnum, User, Template, GenerationTask, TaskStatusEnum
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate, TaskCallbackRequest
router = APIRouter()


def _build_order_response(order, task_id=None):
    return OrderResponse(
        id=str(order.id),
        user_id=str(order.user_id),
        template_id=str(order.template_id) if order.template_id else None,
        task_id=task_id,
        status=order.status.value if hasattr(order.status, 'value') else str(order.status),
        amount=float(order.amount),
        credits_consumed=float(order.credits_consumed) if order.credits_consumed else None,
        result_image_url=getattr(order, 'result_image_url', None),
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def _find_task_for_order(db: Session, order) -> "str | None":
    """Find the most closely matching GenerationTask for an order by timestamp."""
    if not order.template_id:
        return None
    task = (
        db.query(GenerationTask)
        .filter(
            GenerationTask.user_id == order.user_id,
            GenerationTask.template_id == order.template_id,
            GenerationTask.created_at >= order.created_at,
        )
        .order_by(GenerationTask.created_at.asc())
        .first()
    )
    return str(task.id) if task else None


@router.post("/", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    Create a new order with async generation task.
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
        status=OrderStatusEnum.PENDING,
        amount=template_price,
        credits_consumed=template_price,
        credits_purchased=0,
        platform="web",
        result_image_url=settings.DEFAULT_RESULT_IMAGE_PLACEHOLDER
    )

    # Create a generation task
    task = GenerationTask(
        user_id=current_user_id,
        template_id=order_in.template_id,
        status=TaskStatusEnum.PENDING,
    )

    # 更新模板使用次数
    template.usage_count = (template.usage_count or 0) + 1

    db.add(order)
    db.add(task)
    db.commit()
    db.refresh(order)
    db.refresh(task)
    db.refresh(user)
    db.refresh(template)

    return _build_order_response(order, task_id=str(task.id))


@router.post("/tasks/callback")
def task_callback(
    callback: TaskCallbackRequest,
    db: Session = Depends(get_sync_db),
) -> Any:
    """Webhook callback to update task and order status.

    NOTE: In production, secure this endpoint with API key or HMAC verification.
    """
    task = db.query(GenerationTask).filter(GenerationTask.id == callback.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if callback.status == "COMPLETED":
        task.status = TaskStatusEnum.COMPLETED
    elif callback.status == "FAILED":
        task.status = TaskStatusEnum.FAILED
    else:
        raise HTTPException(status_code=400, detail="Invalid status. Must be COMPLETED or FAILED")

    # Find the associated PENDING order created just before or at the same time as the task
    order = (
        db.query(Order)
        .filter(
            Order.user_id == task.user_id,
            Order.template_id == task.template_id,
            Order.status == OrderStatusEnum.PENDING,
            Order.created_at <= task.created_at,
        )
        .order_by(Order.created_at.desc())
        .first()
    )

    order_updated = False
    if order:
        if callback.status == "COMPLETED":
            order.status = OrderStatusEnum.COMPLETED
            if callback.result_image_url:
                order.result_image_url = callback.result_image_url
        elif callback.status == "FAILED":
            order.status = OrderStatusEnum.FAILED
        order_updated = True

    db.commit()
    return {
        "detail": "Callback processed",
        "task_id": callback.task_id,
        "status": callback.status,
        "order_updated": order_updated,
    }


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
    result = []
    for order in orders:
        result.append(_build_order_response(order, task_id=_find_task_for_order(db, order)))
    return result


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
    
    return _build_order_response(order, task_id=_find_task_for_order(db, order))