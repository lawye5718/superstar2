"""Application configuration"""

import os
import secrets
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Superstar AI"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./superstar.db")
    DATABASE_SYNC_URL: str = os.getenv("DATABASE_SYNC_URL", "sqlite:///./superstar.db")
    
    # JWT — default generates a random key; always set SECRET_KEY in production via env
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS — comma-separated origins; defaults to localhost only
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
        if origin.strip()
    ]
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Volcano Engine (AI generation)
    VOLCANO_API_KEY: str = os.getenv("VOLCANO_API_KEY", "")
    VOLCANO_SECRET_KEY: str = os.getenv("VOLCANO_SECRET_KEY", "")

    # Callback authentication — shared secret used by external services to authenticate
    # webhook callbacks. Must be set via CALLBACK_API_KEY env var in production.
    CALLBACK_API_KEY: str = os.getenv("CALLBACK_API_KEY", "")
    
    # Storage
    CDN_DOMAIN: str = os.getenv("CDN_DOMAIN", "")
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, cos, s3, etc.
    
    # Default values
    DEFAULT_TEMPLATE_PRICE: float = 9.9
    DEFAULT_RESULT_IMAGE_PLACEHOLDER: str = "/static/placeholder-result.jpg"
    
    class Config:
        case_sensitive = True


def get_settings():
    """Get application settings"""
    return Settings()


settings = get_settings()