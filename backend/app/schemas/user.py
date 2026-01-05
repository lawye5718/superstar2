"""User schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    username: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    balance: Optional[float] = None
    face_image_url: Optional[str] = None
    gender: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[str] = None
    balance: float = 0.0
    face_image_url: Optional[str] = None
    gender: Optional[str] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class UserResponse(UserInDBBase):
    # 关键修复：显式声明字段，确保 API 返回
    is_superuser: bool
    pass


class UserInDB(UserInDBBase):
    password_hash: str

    class Config:
        from_attributes = True