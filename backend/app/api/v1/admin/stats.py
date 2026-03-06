from fastapi import APIRouter, Depends, Query
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
        from fastapi import HTTPException
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
        db.query(func.count(func.distinct(Order.user_id)))
        .filter(Order.credits_purchased > 0)
        .scalar() or 0
    )

    return AdminStatsResponse(
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_templates=total_templates,
        paid_users=paid_users,
    )


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
