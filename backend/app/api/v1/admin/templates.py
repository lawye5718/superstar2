from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import Template, GenderEnum, User
from app.schemas.template import TemplateResponse
from pydantic import BaseModel


class AdminTemplateCreate(BaseModel):
    title: str
    category: str  # 对应前端的分类
    cover_image_url: str  # 对应前端的封面图
    prompt_config: Optional[Dict[str, Any]] = {}  # 前端的prompt配置
    price: float = 9.9  # 价格


class AdminTemplateUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    cover_image_url: Optional[str] = None
    prompt_config: Optional[Dict[str, Any]] = None
    price: Optional[float] = None
    is_approved: Optional[bool] = None


GENDER_MAP = {
    "MALE": GenderEnum.MALE,
    "FEMALE": GenderEnum.FEMALE,
    "COUPLE": GenderEnum.COUPLE,
    "UNISEX": GenderEnum.UNISEX,
    "Male": GenderEnum.MALE,
    "Female": GenderEnum.FEMALE,
    "Couple": GenderEnum.COUPLE,
    "Unisex": GenderEnum.UNISEX,
}


router = APIRouter()

@router.get("/", response_model=List[TemplateResponse])
def list_templates_admin(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """List all templates for admin (including unapproved)"""
    admin = db.query(User).filter(User.id == current_user_id).first()
    if not admin or not getattr(admin, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    templates = (
        db.query(Template)
        .order_by(Template.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return templates


@router.post("/", response_model=TemplateResponse)
def create_template(
    template_in: AdminTemplateCreate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """
    管理员创建新模版 (Create new template)
    """
    admin = db.query(User).filter(User.id == current_user_id).first()
    if not admin or not getattr(admin, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    gender = GENDER_MAP.get(template_in.category, GenderEnum.UNISEX)
    
    template = Template(
        title=template_in.title,
        gender=gender,
        tags=[template_in.category],
        display_image_urls=[template_in.cover_image_url] if template_in.cover_image_url else [],
        config=template_in.prompt_config if template_in.prompt_config else {},
        price=template_in.price,
        is_approved=True,
        usage_count=0
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: str,
    template_in: AdminTemplateUpdate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id),
) -> Any:
    """Update a template (admin only)"""
    admin = db.query(User).filter(User.id == current_user_id).first()
    if not admin or not getattr(admin, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if template_in.title is not None:
        template.title = template_in.title
    if template_in.category is not None:
        template.gender = GENDER_MAP.get(template_in.category, GenderEnum.UNISEX)
        template.tags = [template_in.category]
    if template_in.cover_image_url is not None:
        template.display_image_urls = [template_in.cover_image_url] if template_in.cover_image_url else []
    if template_in.prompt_config is not None:
        template.config = template_in.prompt_config
    if template_in.price is not None:
        template.price = template_in.price
    if template_in.is_approved is not None:
        template.is_approved = template_in.is_approved

    db.commit()
    db.refresh(template)
    
    return template