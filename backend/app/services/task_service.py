"""Task service"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import GenerationTask
from app.schemas.task import TaskCreate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, task_in: TaskCreate):
        """Create a new generation task"""
        db_task = GenerationTask(
            user_id=task_in.user_id,
            template_id=task_in.template_id,
            status=task_in.status,
            portrait_url=task_in.portrait_url,
            error_message=task_in.error_message
        )
        
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        
        return db_task

    async def get_task_by_id(self, task_id: str) -> Optional[GenerationTask]:
        """Get task by ID"""
        result = await self.db.execute(
            select(GenerationTask).where(GenerationTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[GenerationTask]:
        """Get tasks with pagination"""
        result = await self.db.execute(
            select(GenerationTask).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_task(self, task_id: str, task_in: TaskCreate) -> Optional[GenerationTask]:
        """Update task by ID"""
        db_task = await self.get_task_by_id(task_id)
        if not db_task:
            return None

        # Update fields
        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task