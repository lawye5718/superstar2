"""Order schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.database import OrderStatusEnum


class OrderBase(BaseModel):
    user_id: UUID
    credits_purchased: int
    amount: float
    platform: str
    status: OrderStatusEnum = OrderStatusEnum.PENDING


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: UUID
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True