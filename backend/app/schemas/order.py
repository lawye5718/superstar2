"""Order schemas"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.database import OrderStatusEnum


class OrderBase(BaseModel):
    template_id: Optional[str] = None  # Template ID for the order


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    template_id: str  # Make required for order creation
    
    @field_validator('template_id')
    @classmethod
    def validate_template_id(cls, v):
        """Validate template_id is a valid UUID"""
        if not v or not v.strip():
            raise ValueError('template_id is required')
        # Basic UUID format validation
        try:
            # Check if it's a valid UUID format
            import uuid
            uuid.UUID(v)
        except (ValueError, AttributeError):
            raise ValueError('template_id must be a valid UUID')
        return v.strip()


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatusEnum] = None
    result_image_url: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: str
    user_id: str
    template_id: Optional[str] = None
    status: str
    amount: float
    credits_consumed: Optional[float] = None
    result_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True