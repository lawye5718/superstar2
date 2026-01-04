"""Admin user management API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, List
from pydantic import BaseModel

from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_user_id
from app.models.database import User, Order
from app.schemas.user import UserResponse

router = APIRouter()


class UpdateUserRoleRequest(BaseModel):
    user_id: str
    roles: List[str]


def verify_admin(current_user_id: str = Depends(get_current_user_id)) -> str:
    """Verify if user is admin"""
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user or "admin" not in (user.roles or []):
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user_id
    finally:
        db.close()


@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user_id: str = Depends(verify_admin)
) -> Any:
    """List all users (admin only)"""
    db = SyncSessionLocal()
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    finally:
        db.close()


@router.post("/users/role")
def update_user_role(
    req: UpdateUserRoleRequest,
    current_user_id: str = Depends(verify_admin)
) -> Any:
    """Update user roles (admin only)"""
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.id == req.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.roles = req.roles
        db.commit()
        
        return {"status": "success", "user_id": req.user_id, "roles": req.roles}
    finally:
        db.close()


@router.get("/stats")
def get_admin_stats(
    current_user_id: str = Depends(verify_admin)
) -> Any:
    """Get admin statistics"""
    db = SyncSessionLocal()
    try:
        user_count = db.query(User).count()
        order_count = db.query(Order).count()
        
        # Get orders with status breakdown
        completed_orders = db.query(Order).filter(Order.status == "COMPLETED").count()
        pending_orders = db.query(Order).filter(Order.status == "PENDING").count()
        
        return {
            "total_users": user_count,
            "total_orders": order_count,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders
        }
    finally:
        db.close()
