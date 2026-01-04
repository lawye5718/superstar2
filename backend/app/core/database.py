"""Database configuration and session management"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager
import logging

from .config import get_settings

settings = get_settings()

# Synchronous engine for Alembic migrations and sync operations
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    # 动态配置连接参数，仅在使用SQLite时添加check_same_thread
    **{"connect_args": {"check_same_thread": False}} if settings.DATABASE_SYNC_URL.startswith("sqlite") else {}
)

# Asynchronous engine for FastAPI operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    # 动态配置连接参数，仅在使用SQLite时添加check_same_thread
    **{"connect_args": {"check_same_thread": False}} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Session factories
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    expire_on_commit=False,
    class_=AsyncSession,
    bind=async_engine
)

Base = declarative_base()


# Dependency for FastAPI
async def get_db() -> AsyncSession:
    """Get database session as FastAPI dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database connection and create tables"""
    try:
        # Import all models to ensure they are registered with Base
        from app.models import database  # This imports all models
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logging.info("Database connection initialized and tables created successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connection"""
    await async_engine.dispose()
    logging.info("Database connection closed")