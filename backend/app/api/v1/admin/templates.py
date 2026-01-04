from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.dependencies import get_db
from app.models.database import Template
from app.schemas.template import TemplateResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.models.database import GenderEnum


class AdminTemplateCreate(BaseModel):
    title: str
    category: str  # 对应前端的分类
    cover_image_url: str  # 对应前端的封面图
    prompt_config: Optional[Dict[str, Any]] = {}  # 前端的prompt配置
    price: float = 9.9  # 价格


router = APIRouter()

@router.post("/", response_model=TemplateResponse)
def create_template(
    template_in: AdminTemplateCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    管理员创建新模版 (Create new template)
    """
    # 简单的创建逻辑
    template = Template(
        title=template_in.title,
        # 为兼容现有数据库模型，将category映射到gender字段
        gender=template_in.category.upper() if template_in.category.upper() in [e.value for e in GenderEnum] else 'UNISEX',
        tags=[template_in.category],
        display_image_urls=[template_in.cover_image_url] if template_in.cover_image_url else [],
        config=template_in.prompt_config if template_in.prompt_config else {},
        price=template_in.price if hasattr(template_in, 'price') else 9.9,
        is_approved=True,
        usage_count=0
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template