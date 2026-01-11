"""Application configuration"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Superstar AI"
    API_V1_STR: str = "/api/v1"
    
    # 1. 安全配置 (必须从环境变量读取)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "unsafe_development_key_change_me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7天
    
    # 2. CORS 配置 (允许前端访问)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        "*" 
    ]

    # 3. 数据库配置 (优先使用 Postgres)
    # 默认值适配 docker-compose 中的 Postgres
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/superstar"
    )

    # 4. 基础设施
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # 5. 域名配置 (解决图片 URL 问题)
    DOMAIN: str = os.getenv("DOMAIN", "http://localhost:8000")

    class Config:
        case_sensitive = True

settings = Settings()
