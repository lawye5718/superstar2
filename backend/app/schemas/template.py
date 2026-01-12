"""Template schemas"""

from pydantic import BaseModel, model_validator
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
    price: Optional[float] = None  # Will use DEFAULT_TEMPLATE_PRICE from config if None
    usage_count: Optional[int] = 0


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
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 新增：计算属性，供前端直接使用
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True

    # 使用 Pydantic 的 model_validator 来填充 cover_image_url
    @model_validator(mode='after')
    def set_cover_image(self):
        if self.display_image_urls and len(self.display_image_urls) > 0:
            self.cover_image_url = self.display_image_urls[0]
        else:
            # 设置一个默认占位图
            self.cover_image_url = "https://via.placeholder.com/400x600?text=No+Image"
        return self