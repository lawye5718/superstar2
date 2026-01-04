"""Gallery schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class GalleryBase(BaseModel):
    user_id: UUID
    template_id: UUID
    image_url_free: str
    is_public: bool = False
    image_url_paid: Optional[str] = None
    thumbnail_url: Optional[str] = None


class GalleryCreate(GalleryBase):
    pass


class GalleryResponse(GalleryBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True