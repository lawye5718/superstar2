from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db, get_current_active_user
from app.models import User, Order

router = APIRouter()

@router.get("/dashboard", response_model=dict)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    total_users = db.query(User).count()
    # 统计已完成订单的总收入
    total_revenue = db.query(func.sum(Order.amount)).filter(Order.status == 'COMPLETED').scalar() or 0.0
    total_orders = db.query(Order).count()

    return {
        "total_users": total_users,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders
    }

