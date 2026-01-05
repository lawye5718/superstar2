from typing import List
from pydantic import BaseModel

from app.schemas.user import UserResponse


class AdminStatsResponse(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    total_templates: int
    paid_users: int


class AdminUserListResponse(BaseModel):
    total: int
    items: List[UserResponse]
