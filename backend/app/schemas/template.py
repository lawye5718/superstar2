"""Template schemas"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.database import GenderEnum


class TemplateBase(BaseModel):
    title: str
    gender: GenderEnum
    tags: List[str]
    config: Dict[str, Any]
    is_approved: Optional[bool] = False
    display_image_urls: List[str]


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    gender: Optional[GenderEnum] = None
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    is_approved: Optional[bool] = None
    display_image_urls: Optional[List[str]] = None


class TemplateResponse(TemplateBase):
    id: UUID
    price: float = 9.9
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True