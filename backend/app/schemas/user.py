"""User schemas"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None


class UserCreate(UserBase):
    email: str
    password: str


class UserUpdate(UserBase):
    credits: Optional[float] = None
    balance: Optional[float] = None
    face_image_url: Optional[str] = None
    gender: Optional[str] = None


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