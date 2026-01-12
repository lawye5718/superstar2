from datetime import timedelta
from fastapi import APIRouter, Depends, Form, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_sync_db
from app.core.dependencies import create_access_token
from app.core.security import verify_password
from app.models.database import User
from app.core.rate_limiter import limiter # ✅ 引入限流器


router = APIRouter()


@router.post("/login/access-token")
@limiter.limit("5/minute") # ✅ 严格安全：每IP每分钟限制5次登录尝试
def login_access_token(
    request: Request, # 必须添加 request 参数供 limiter 使用
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_sync_db),
):
    """Username/password login with Rate Limiting"""
    user = db.query(User).filter(User.email == username).first()
    
    # 防止时序攻击
    is_valid = False
    if user and user.password_hash:
        is_valid = verify_password(password, user.password_hash)
    else:
        verify_password(password, "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
