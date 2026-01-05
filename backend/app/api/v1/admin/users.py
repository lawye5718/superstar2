from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import SyncSessionLocal
from app.core.dependencies import get_current_active_superuser, get_db
from app.models.database import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.patch("/{user_id}/set-superuser", response_model=UserResponse)
def set_user_superuser(
    user_id: str,
    is_superuser: bool,
    current_user = Depends(get_current_active_superuser),
    db: Session = Depends(SyncSessionLocal)
) -> Any:
    """
    设置用户为超级用户(管理员)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_superuser = is_superuser
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/list", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_superuser),
    db: Session = Depends(SyncSessionLocal)
) -> Any:
    """
    列出所有用户(仅管理员)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/stats", response_model=dict)
def get_user_stats(
    current_user = Depends(get_current_active_superuser),
    db: Session = Depends(SyncSessionLocal)
) -> Any:
    """
    获取用户统计信息(仅管理员)
    """
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    superusers = db.query(User).filter(User.is_superuser == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "superusers": superusers
    }