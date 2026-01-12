"""FastAPI application entry point"""

from contextlib import asynccontextmanager
from pathlib import Path
import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1 import router as api_v1_router
from app.core.database import engine, Base
from app.core.rate_limiter import limiter, rate_limit_handler
from app.core.exceptions import SuperstarException
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    superstar_exception_handler,
    general_exception_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="2.1.0"
)

# 1. 注册限流器 (Rate Limiter)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# 2. Register error handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SuperstarException, superstar_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 3. CORS 配置应用
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. 静态文件挂载
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 5. 注册路由
app.include_router(api_v1_router.api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Superstar AI API is running", "version": "2.1.0"}


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if service is healthy.
    """
    try:
        # Test database connectivity
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "version": "2.1.0",
            "service": "Superstar AI"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)