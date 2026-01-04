"""Task schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.database import TaskStatusEnum


class TaskBase(BaseModel):
    user_id: UUID
    template_id: UUID
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    portrait_url: Optional[str] = None
    error_message: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: UUID
    result_gallery_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True