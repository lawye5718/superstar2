from datetime import timedelta
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_sync_db
from app.core.dependencies import create_access_token
from app.core.security import verify_password
from app.models.database import User


router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_sync_db),
):
    """Username/password login to exchange for JWT token"""
    user = db.query(User).filter(User.email == username).first()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": user.id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
