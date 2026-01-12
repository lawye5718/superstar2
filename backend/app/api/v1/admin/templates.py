from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from app.core.dependencies import get_db, get_current_active_user
from app.models import Template, User
from app.schemas import template as template_schemas
from app.models.database import GenderEnum

router = APIRouter()

@router.post("/", response_model=template_schemas.TemplateResponse)
def create_template(
    template_in: template_schemas.TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permission denied")
    template = Template(**template_in.model_dump(), usage_count=0)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{id}", response_model=dict)
def delete_template(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permission denied")
    template = db.query(Template).filter(Template.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(template)
    db.commit()
    return {"status": "success"}

@router.put("/{id}", response_model=template_schemas.TemplateResponse)
def update_template(
    id: int,
    template_in: template_schemas.TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Permission denied")
    
    template = db.query(Template).filter(Template.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 更新模板信息
    for field, value in template_in.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template
