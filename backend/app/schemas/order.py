"""Order schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.database import OrderStatusEnum


class OrderBase(BaseModel):
    template_id: Optional[str] = None  # Template ID for the order


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    pass


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatusEnum] = None
    result_image_url: Optional[str] = None


class TaskCallbackRequest(BaseModel):
    """Schema for task callback webhook"""
    task_id: str
    status: str  # COMPLETED or FAILED
    result_image_url: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: str
    user_id: str
    template_id: Optional[str] = None
    task_id: Optional[str] = None
    status: str
    amount: float
    credits_consumed: Optional[float] = None
    result_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True