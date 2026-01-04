"""Task API routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new generation task"""
    task_service = TaskService(db)
    task = await task_service.create_task(task_in)
    return task


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get tasks with pagination"""
    task_service = TaskService(db)
    tasks = await task_service.get_tasks(skip=skip, limit=limit)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get task by ID"""
    task_service = TaskService(db)
    task = await task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Update task by ID"""
    task_service = TaskService(db)
    task = await task_service.update_task(task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task