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
            # 如果没有模板，返回一个模拟的模板
            return TemplateResponse(
                id="mock-template-id",
                title="军绿色毛呢大衣复古写真",
                gender="Female",
                tags=["复古", "大衣", "冬季"],
                config={
                    "base_prompt": "High quality, 8k resolution, masterpiece",
                    "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
                    "negative_prompt": "bad anatomy"
                },
                is_approved=True,
                display_image_urls=["https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500&q=80"],
                price=9.9,
                usage_count=1250
            )
        
        # 随机获取一个偏移量
        random_offset = random.randint(0, total_count - 1)
        template = db.query(Template).offset(random_offset).first()
        
        # 转换为响应模型
        return TemplateResponse(
            id=str(template.id),
            title=template.title,
            gender=template.gender.value if template.gender else "Unisex",
            tags=template.tags or [],
            config=template.config or {},
            is_approved=template.is_approved,
            display_image_urls=template.display_image_urls or [],
            price=getattr(template, 'price', 9.9),  # 假设模板有价格属性
            usage_count=getattr(template, 'usage_count', 0)  # 假设模板有使用次数属性
        )
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
            # 简单的分类过滤，实际实现可能需要更复杂的逻辑
            pass  # 这里可以添加分类过滤逻辑
        
        templates = query.offset(skip).limit(limit).all()
        
        # 转换为响应模型列表
        result = []
        for template in templates:
            result.append(TemplateResponse(
                id=str(template.id),
                title=template.title,
                gender=template.gender.value if template.gender else "Unisex",
                tags=template.tags or [],
                config=template.config or {},
                is_approved=template.is_approved,
                display_image_urls=template.display_image_urls or [],
                price=getattr(template, 'price', 9.9),  # 假设模板有价格属性
                usage_count=getattr(template, 'usage_count', 0)  # 假设模板有使用次数属性
            ))
        
        return result
    finally:
        db.close()