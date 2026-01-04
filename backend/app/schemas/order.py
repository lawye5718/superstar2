"""Order schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.database import OrderStatusEnum


class OrderBase(BaseModel):
    template_id: Optional[UUID] = None


class OrderCreate(BaseModel):
    template_id: UUID


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    template_id: Optional[UUID] = None
    status: str
    amount: float
    credits_consumed: float
    result_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True