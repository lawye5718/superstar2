"""API v1 router"""

from fastapi import APIRouter
from . import users, templates, orders, utils
from .admin import templates as admin_templates

api_router = APIRouter()

# Include API routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

# 通用/工具接口
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

# 管理员接口 (建议加权限验证，这里MVP略过)
api_router.include_router(admin_templates.router, prefix="/admin/templates", tags=["admin"])