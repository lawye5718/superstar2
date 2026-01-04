"""User schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    credits: Optional[int] = None


class UserResponse(UserBase):
    id: UUID
    credits: int
    roles: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True