from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import Order, Template, User
from app.schemas.admin import AdminStatsResponse, AdminUserListResponse

router = APIRouter()


def _require_admin(db: Session, user_id: str):
    admin = db.query(User).filter(User.id == user_id).first()
    if not admin or not getattr(admin, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return admin


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """运营与用户统计"""
    _require_admin(db, current_user_id)

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Order.amount), 0)).scalar() or 0
    total_templates = db.query(func.count(Template.id)).scalar() or 0
    paid_users = (
        db.query(func.count(func.distinct(Order.user_id))).filter(Order.amount > 0).scalar() or 0
    )

    return AdminStatsResponse(
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_templates=total_templates,
        paid_users=paid_users,
    )


@router.get("/stats/dashboard", response_model=dict)
def get_admin_dashboard_stats(
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """实时运营数据看板"""
    _require_admin(db, current_user_id)

    # 1. 总用户数
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    # 2. 总收入 (所有 COMPLETED 订单的金额总和)
    total_revenue = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(Order.status == 'COMPLETED').scalar() or 0
    
    # 3. 总订单数
    total_orders = db.query(func.count(Order.id)).filter(Order.status.in_(['COMPLETED', 'PENDING', 'PROCESSING'])).scalar() or 0
    
    # 4. 模板数量
    total_templates = db.query(func.count(Template.id)).scalar() or 0

    return {
        "total_users": total_users,
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": total_orders,
        "total_templates": total_templates
    }


@router.get("/users", response_model=AdminUserListResponse)
def list_users_for_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """管理员获取用户列表"""
    _require_admin(db, current_user_id)

    base_query = db.query(User).order_by(User.created_at.desc())
    total = base_query.count()
    users = base_query.offset(skip).limit(limit).all()
    return AdminUserListResponse(total=total, items=users)
