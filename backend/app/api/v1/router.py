"""API v1 router"""

from fastapi import APIRouter
from . import users, templates, orders, galleries, tasks

api_router = APIRouter()

# Include API routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(galleries.router, prefix="/galleries", tags=["galleries"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])