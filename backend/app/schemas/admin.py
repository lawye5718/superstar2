from typing import List, Optional
from pydantic import BaseModel

from app.schemas.user import UserResponse


class TopTemplateItem(BaseModel):
    id: str
    title: str
    usage_count: int
    price: float


class AdminStatsResponse(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    total_templates: int
    paid_users: int
    top_templates: List[TopTemplateItem] = []


class AdminUserListResponse(BaseModel):
    total: int
    items: List[UserResponse]
