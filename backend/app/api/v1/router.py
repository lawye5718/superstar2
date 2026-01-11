from fastapi import APIRouter
from app.api.v1 import users, orders, templates, utils, tasks, galleries, auth
from app.api.v1.admin import templates as admin_templates
from app.api.v1.admin import stats as admin_stats # ✅ 导入 Stats

api_router = APIRouter()

# 基础功能
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

# 用户业务
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(galleries.router, prefix="/galleries", tags=["galleries"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# 管理员业务
api_router.include_router(admin_templates.router, prefix="/admin/templates", tags=["admin"])
api_router.include_router(admin_stats.router, prefix="/admin/stats", tags=["admin"]) # ✅ 注册路由