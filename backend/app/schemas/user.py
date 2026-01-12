"""User schemas"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="密码至少8位")

    # ✅ 严格修复：强制密码复杂度 (数字+大写字母+8位以上)
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v):
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserUpdate(UserBase):
    credits: Optional[float] = None
    balance: Optional[float] = None


class UserResponse(UserBase):
    id: str
    credits: float
    balance: float
    face_image_url: Optional[str] = None
    gender: Optional[str] = None
    is_superuser: bool = False
    roles: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
