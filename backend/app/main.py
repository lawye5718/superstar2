"""FastAPI application entry point"""

from contextlib import asynccontextmanager
from pathlib import Path
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1 import router as api_v1_router
from app.core.database import engine, Base
from app.core.rate_limiter import limiter, rate_limit_handler # ✅ 新增导入

# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 1. 注册限流器 (Rate Limiter)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler) # ✅ 注册异常处理

# 2. CORS 配置应用
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 静态文件挂载
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. 注册路由
app.include_router(api_v1_router.api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Superstar AI API is running", "version": "2.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)