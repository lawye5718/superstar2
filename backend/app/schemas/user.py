"""User schemas"""

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None


class UserCreate(UserBase):
    email: str
    password: str

    # ✅ 新增：密码复杂度验证
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[A-Z]", v):
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
