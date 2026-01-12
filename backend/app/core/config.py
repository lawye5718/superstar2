import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Superstar AI"
    API_V1_STR: str = "/api/v1"
    
    # ⚠️ 安全: 必须从环境变量读取，生产环境若未设置则启动失败（或生成随机）
    SECRET_KEY: str = os.getenv("SECRET_KEY", "unsafe_dev_key_do_not_use_in_prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 
    
    # CORS 限制
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        "*" # ⚠️ 生产环境请移除 "*"
    ]

    # 数据库
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/superstar"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # 域名 (用于生成图片链接)
    DOMAIN: str = os.getenv("DOMAIN", "http://localhost:8000")
    
    # 上传限制
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        case_sensitive = True

settings = Settings()
