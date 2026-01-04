"""Application configuration"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Superstar AI"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/superstar_db")
    DATABASE_SYNC_URL: str = os.getenv("DATABASE_SYNC_URL", "postgresql://user:password@localhost/superstar_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Should be restricted in production
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Volcano Engine (AI generation)
    VOLCANO_API_KEY: str = os.getenv("VOLCANO_API_KEY", "")
    VOLCANO_SECRET_KEY: str = os.getenv("VOLCANO_SECRET_KEY", "")
    
    # Storage
    CDN_DOMAIN: str = os.getenv("CDN_DOMAIN", "")
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, cos, s3, etc.
    
    class Config:
        case_sensitive = True


def get_settings():
    """Get application settings"""
    return Settings()


settings = get_settings()