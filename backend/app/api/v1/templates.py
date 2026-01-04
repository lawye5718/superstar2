"""Template API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter()


@router.post("/", response_model=TemplateResponse)
async def create_template(template_in: TemplateCreate, db: AsyncSession = Depends(get_db)):
    """Create a new template"""
    template_service = TemplateService(db)
    template = await template_service.create_template(template_in)
    return template


@router.get("/", response_model=List[TemplateResponse])
async def get_templates(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get templates with pagination"""
    template_service = TemplateService(db)
    templates = await template_service.get_templates(skip=skip, limit=limit)
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: AsyncSession = Depends(get_db)):
    """Get template by ID"""
    template_service = TemplateService(db)
    template = await template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, template_in: TemplateUpdate, db: AsyncSession = Depends(get_db)):
    """Update template by ID"""
    template_service = TemplateService(db)
    template = await template_service.update_template(template_id, template_in)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}")
async def delete_template(template_id: str, db: AsyncSession = Depends(get_db)):
    """Delete template by ID"""
    template_service = TemplateService(db)
    success = await template_service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}