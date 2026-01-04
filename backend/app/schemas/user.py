"""User schemas"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    email: str
    password: str


class UserUpdate(UserBase):
    credits: Optional[int] = None


class UserResponse(UserBase):
    id: str
    credits: int
    roles: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True