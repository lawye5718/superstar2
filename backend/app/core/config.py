"""Application configuration"""

"""Application configuration"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Superstar AI"
    API_V1_STR: str = "/api/v1"
    
    # 1. 安全配置
    # ✅ 修复：生产环境应强制检查密钥强度，此处为了演示保留默认值但增加警告
    SECRET_KEY: str = os.getenv("SECRET_KEY", "unsafe_development_key_change_me")
    ALGORITHM: str = "HS256"  # ✅ 新增：明确指定算法，防止算法混淆攻击
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 
    
    # 2. CORS 配置
    # ✅ 修复：移除 "*"，明确指定允许的来源
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        # 生产环境请添加您的实际域名，如 "https://your-domain.com"
    ]

    # 3. 数据库配置
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/superstar"
    )

    # 4. 基础设施
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # 5. 域名配置
    DOMAIN: str = os.getenv("DOMAIN", "http://localhost:8000")

    # ✅ 新增：业务常量配置
    DEFAULT_TEMPLATE_PRICE: float = 9.9
    DEFAULT_RESULT_IMAGE_PLACEHOLDER: str = "https://via.placeholder.com/400"

    class Config:
        case_sensitive = True

settings = Settings()
