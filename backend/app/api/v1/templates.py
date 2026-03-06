"""Template API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any
import random

from app.core.database import get_sync_db
from app.models.database import Template
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateUpdate
router = APIRouter()


@router.get("/random", response_model=TemplateResponse)
def get_random_template(
    db: Session = Depends(get_sync_db),
) -> Any:
    """
    Get a random template.
    """
    total_count = db.query(Template).count()
    if total_count == 0:
        raise HTTPException(status_code=404, detail="No templates found")
    
    random_offset = random.randint(0, total_count - 1)
    template = db.query(Template).offset(random_offset).first()
    
    return template


@router.get("/", response_model=list[TemplateResponse])
def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category: str = Query(None),
    db: Session = Depends(get_sync_db),
) -> Any:
    """
    Get templates with pagination and optional category filter.
    """
    query = db.query(Template).filter(Template.is_approved == True)
    
    if category and category != '全部':
        query = query.filter(Template.tags.contains([category]))
    
    templates = query.offset(skip).limit(limit).all()
    
    return templates