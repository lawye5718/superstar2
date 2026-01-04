"""API v1 router"""

from fastapi import APIRouter
from . import users, orders, templates, utils, auth
from .admin import templates as admin_templates

api_router = APIRouter()

# 核心认证接口 (Login) - 修复点：之前漏掉了
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 用户侧接口
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])

# 通用/工具接口
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

# 管理员接口
api_router.include_router(admin_templates.router, prefix="/admin/templates", tags=["admin"])