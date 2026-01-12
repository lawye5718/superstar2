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
    """Username/password login"""
    user = db.query(User).filter(User.email == username).first()
    
    # ✅ 修复：防止时序攻击，无论用户是否存在都执行一次密码校验（可用任意假hash）
    is_valid = False
    if user and user.password_hash:
        is_valid = verify_password(password, user.password_hash)
    else:
        # 执行一个假的校验来消耗相同的时间，防止攻击者通过响应时间猜出用户是否存在
        verify_password(password, "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")

    if not is_valid:
        # ✅ 修复：返回 401 Unauthorized 而不是 400
        # ✅ 修复：使用通用错误信息，不提示"用户不存在"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": str(user.id)}, # 确保 ID 是字符串
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
