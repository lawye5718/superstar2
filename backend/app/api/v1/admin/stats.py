from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_active_superuser
from app.models.database import Order, Template

router = APIRouter()


@router.get("/overview", response_model=dict)
def get_admin_overview(
    current_user = Depends(get_current_active_superuser),
    db: Session = Depends(SyncSessionLocal)
) -> Any:
    """
    获取管理员总览数据(仅管理员)
    """
    total_orders = db.query(Order).count()
    total_templates = db.query(Template).count()
    
    # 统计最近的订单
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    
    # 计算总收入
    total_revenue = 0.0
    for order in recent_orders:
        total_revenue += float(order.amount) if order.amount else 0.0
    
    return {
        "total_orders": total_orders,
        "total_templates": total_templates,
        "total_revenue": total_revenue,
        "recent_orders_count": len(recent_orders)
    }