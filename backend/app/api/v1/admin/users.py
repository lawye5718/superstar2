import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.admin.stats import _require_admin
from app.api.v1.helpers import normalize_balance_payload
from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import User
from app.schemas.user import UserUpdate, UserResponse

router = APIRouter()


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_by_admin(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Admin can adjust user profile and balance."""
    _require_admin(db, current_user_id)

    try:
        _ = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = normalize_balance_payload(user_in.model_dump(exclude_unset=True))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
