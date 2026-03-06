"""API v1 router"""

from fastapi import APIRouter
from . import users, orders, templates, utils, auth, favorites, packages
from .admin import templates as admin_templates, stats as admin_stats, users as admin_users, packages as admin_packages

api_router = APIRouter()

# 核心认证接口 (Login)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 用户侧接口
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(packages.router, prefix="/packages", tags=["packages"])

# 通用/工具接口
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

# 管理员接口
api_router.include_router(admin_templates.router, prefix="/admin/templates", tags=["admin"])
api_router.include_router(admin_stats.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin"])
api_router.include_router(admin_packages.router, prefix="/admin/packages", tags=["admin"])