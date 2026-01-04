"""Gallery API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.gallery import GalleryCreate, GalleryResponse
from app.services.gallery_service import GalleryService

router = APIRouter()


@router.post("/", response_model=GalleryResponse)
async def create_gallery(gallery_in: GalleryCreate, db: AsyncSession = Depends(get_db)):
    """Create a new gallery item"""
    gallery_service = GalleryService(db)
    gallery = await gallery_service.create_gallery(gallery_in)
    return gallery


@router.get("/", response_model=List[GalleryResponse])
async def get_galleries(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get galleries with pagination"""
    gallery_service = GalleryService(db)
    galleries = await gallery_service.get_galleries(skip=skip, limit=limit)
    return galleries


@router.get("/{gallery_id}", response_model=GalleryResponse)
async def get_gallery(gallery_id: str, db: AsyncSession = Depends(get_db)):
    """Get gallery by ID"""
    gallery_service = GalleryService(db)
    gallery = await gallery_service.get_gallery_by_id(gallery_id)
    if not gallery:
        raise HTTPException(status_code=404, detail="Gallery not found")
    return gallery