from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import get_sync_db
from app.core.dependencies import get_current_user_id
from app.models.database import Template, GenderEnum, User
from app.schemas.template import TemplateResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any as AnyType


class AdminTemplateCreate(BaseModel):
    title: str
    category: str  # 对应前端的分类
    cover_image_url: str  # 对应前端的封面图
    prompt_config: Optional[Dict[str, AnyType]] = {}  # 前端的prompt配置
    price: float = 9.9  # 价格


router = APIRouter()

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

    # Map category string to GenderEnum
    gender_map = {
        "MALE": GenderEnum.MALE,
        "FEMALE": GenderEnum.FEMALE,
        "COUPLE": GenderEnum.COUPLE,
        "UNISEX": GenderEnum.UNISEX,
        "Male": GenderEnum.MALE,
        "Female": GenderEnum.FEMALE,
        "Couple": GenderEnum.COUPLE,
        "Unisex": GenderEnum.UNISEX,
    }
    
    gender = gender_map.get(template_in.category, GenderEnum.UNISEX)
    
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