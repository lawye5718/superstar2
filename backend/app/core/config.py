import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Superstar AI"
    API_V1_STR: str = "/api/v1"
    
    # ⚠️ 安全: 必须从环境变量读取，生产环境若未设置则启动失败（或生成随机）
    SECRET_KEY: str = os.getenv("SECRET_KEY", "unsafe_dev_key_do_not_use_in_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 
    
    # CORS 限制
    # ⚠️ 生产环境安全提示：
    # 1. 移除 "*" 并仅允许受信任的域名
    # 2. 示例：["https://app.superstar.ai", "https://www.superstar.ai"]
    # 3. 建议使用环境变量配置：os.getenv("CORS_ORIGINS", "").split(",")
    _cors_origins_str = os.getenv("CORS_ORIGINS", "")
    if _cors_origins_str:
        # Production: Use environment variable
        BACKEND_CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins_str.split(",") if origin.strip()]
    else:
        # Development: Allow localhost and wildcard (NOT SAFE FOR PRODUCTION)
        BACKEND_CORS_ORIGINS: List[str] = [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost",
            "*"  # ⚠️ Remove this in production
        ]

    # 数据库
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/superstar"
    )
    
    # Database URL alias for consistency
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URL
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # 域名 (用于生成图片链接)
    DOMAIN: str = os.getenv("DOMAIN", "http://localhost:8000")
    
    # 上传限制
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 火山引擎配置
    VOLC_API_URL: str = os.getenv("VOLC_API_URL", "https://ark.cn-beijing.volces.com/api/v3/images/generations")
    VOLC_MODEL_ID: str = os.getenv("VOLC_MODEL_ID", "doubao-seedream-4.0")
    VOLC_API_KEY: str = os.getenv("VOLC_API_KEY", "")
    VOLC_ACCESS_KEY: str = os.getenv("VOLC_ACCESS_KEY", "")
    VOLC_SECRET_KEY: str = os.getenv("VOLC_SECRET_KEY", "")
    VOLC_REGION: str = os.getenv("VOLC_REGION", "cn-north-1")
    
    # 腾讯云COS配置
    COS_SECRET_ID: str = os.getenv("COS_SECRET_ID", "")
    COS_SECRET_KEY: str = os.getenv("COS_SECRET_KEY", "")
    COS_REGION: str = os.getenv("COS_REGION", "ap-beijing")
    COS_BUCKET: str = os.getenv("COS_BUCKET", "")

    class Config:
        case_sensitive = True

settings = Settings()
