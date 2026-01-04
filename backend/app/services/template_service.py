"""Template service"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Template
from app.schemas.template import TemplateCreate, TemplateUpdate


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(self, template_in: TemplateCreate):
        """Create a new template"""
        db_template = Template(
            title=template_in.title,
            gender=template_in.gender,
            tags=template_in.tags,
            config=template_in.config,
            is_approved=template_in.is_approved,
            display_image_urls=template_in.display_image_urls
        )
        
        self.db.add(db_template)
        await self.db.commit()
        await self.db.refresh(db_template)
        
        return db_template

    async def get_template_by_id(self, template_id: str) -> Optional[Template]:
        """Get template by ID"""
        result = await self.db.execute(
            select(Template).where(Template.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_templates(self, skip: int = 0, limit: int = 100) -> List[Template]:
        """Get templates with pagination"""
        result = await self.db.execute(
            select(Template).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_template(self, template_id: str, template_in: TemplateUpdate) -> Optional[Template]:
        """Update template by ID"""
        db_template = await self.get_template_by_id(template_id)
        if not db_template:
            return None

        # Update fields if provided
        update_data = template_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)

        await self.db.commit()
        await self.db.refresh(db_template)
        return db_template

    async def delete_template(self, template_id: str) -> bool:
        """Delete template by ID"""
        db_template = await self.get_template_by_id(template_id)
        if not db_template:
            return False

        await self.db.delete(db_template)
        await self.db.commit()
        return True