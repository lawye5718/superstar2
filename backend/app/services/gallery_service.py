"""Gallery service"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import UserGallery
from app.schemas.gallery import GalleryCreate


class GalleryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_gallery(self, gallery_in: GalleryCreate):
        """Create a new gallery item"""
        db_gallery = UserGallery(
            user_id=gallery_in.user_id,
            template_id=gallery_in.template_id,
            image_url_free=gallery_in.image_url_free,
            image_url_paid=gallery_in.image_url_paid,
            thumbnail_url=gallery_in.thumbnail_url,
            is_public=gallery_in.is_public
        )
        
        self.db.add(db_gallery)
        await self.db.commit()
        await self.db.refresh(db_gallery)
        
        return db_gallery

    async def get_gallery_by_id(self, gallery_id: str) -> Optional[UserGallery]:
        """Get gallery by ID"""
        result = await self.db.execute(
            select(UserGallery).where(UserGallery.id == gallery_id)
        )
        return result.scalar_one_or_none()

    async def get_galleries(self, skip: int = 0, limit: int = 100) -> List[UserGallery]:
        """Get galleries with pagination"""
        result = await self.db.execute(
            select(UserGallery).offset(skip).limit(limit)
        )
        return result.scalars().all()