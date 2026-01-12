"""Template schemas"""

from pydantic import BaseModel, model_validator, field_validator
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
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate template title"""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Title must be at least 2 characters')
        if len(v.strip()) > 200:
            raise ValueError('Title must not exceed 200 characters')
        return v.strip()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate template tags"""
        if not isinstance(v, list):
            raise ValueError('Tags must be a list')
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        # Remove empty tags and validate each tag
        valid_tags = []
        for tag in v:
            if tag and tag.strip():
                if len(tag.strip()) > 50:
                    raise ValueError('Each tag must not exceed 50 characters')
                valid_tags.append(tag.strip())
        return valid_tags
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Validate template price"""
        if v is not None:
            if v < 0:
                raise ValueError('Price must be non-negative')
            if v > 9999.99:
                raise ValueError('Price must not exceed 9999.99')
        return v
    
    @field_validator('config')
    @classmethod
    def validate_config(cls, v):
        """Validate template configuration"""
        if not isinstance(v, dict):
            raise ValueError('Config must be a dictionary')
        # Add any specific config validation here
        return v


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    gender: Optional[GenderEnum] = None
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    is_approved: Optional[bool] = None
    display_image_urls: Optional[List[str]] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate template title if provided"""
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty')
            if len(v.strip()) < 2:
                raise ValueError('Title must be at least 2 characters')
            if len(v.strip()) > 200:
                raise ValueError('Title must not exceed 200 characters')
        return v.strip() if v else None


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