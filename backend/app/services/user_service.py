# 新建文件: backend/app/services/user_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.database import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_in: UserCreate) -> User:
        """
        创建新用户，包含重复检查和默认值设置
        """
        existing_user = self.db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists."
            )
        
        # ✅ 优化：注册默认赠送 0 积分 (之前是 100)，防止薅羊毛
        # 如果需要赠送，建议通过 promotion_code 逻辑实现
        initial_credits = 0.0 

        user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            username=user_in.username or user_in.email.split("@")[0],
            credits=initial_credits,
            is_active=True,
            roles=["user"],
            is_superuser=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def top_up_balance(self, user_id: str, amount: float) -> User:
        """
        余额充值逻辑
        """
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
            
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 使用 float 转换确保计算正确
        current_balance = float(user.credits or 0)
        user.credits = current_balance + amount
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_face_info(self, user_id: str, file_url: str, gender: str) -> None:
        """
        更新用户头像和性别
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.face_image_url = file_url
        user.gender = gender
        self.db.commit()