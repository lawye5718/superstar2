"""Template API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any
import random

from app.core.database import SyncSessionLocal
from app.models.database import Template
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateUpdate

router = APIRouter()


@router.get("/random", response_model=TemplateResponse)
def get_random_template() -> Any:
    """
    Get a random template.
    """
    # 使用同步会话以兼容现有代码
    db = SyncSessionLocal()
    try:
        # 获取所有模板数量
        total_count = db.query(Template).count()
        if total_count == 0:
            raise HTTPException(status_code=404, detail="No templates found")
        
        # 随机获取一个偏移量
        random_offset = random.randint(0, total_count - 1)
        template = db.query(Template).offset(random_offset).first()
        
        # 直接返回模型，Pydantic会自动转换
        return template
    finally:
        db.close()


@router.get("/", response_model=list[TemplateResponse])
def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category: str = Query(None)
) -> Any:
    """
    Get templates with pagination and optional category filter.
    """
    # 使用同步会话以兼容现有代码
    db = SyncSessionLocal()
    try:
        query = db.query(Template).filter(Template.is_approved == True)
        
        if category and category != '全部':
            # 根据tags字段过滤分类，使用LIKE查询JSON数组
            from sqlalchemy import text
            query = query.filter(text("tags LIKE :category_pattern").params(category_pattern=f'%{category}%'))
        
        templates = query.offset(skip).limit(limit).all()
        
        # 直接返回模型列表，Pydantic会自动转换
        return templates
    finally:
        db.close()