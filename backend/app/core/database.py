"""Database configuration and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 自动判断数据库类型配置参数
connect_args = {}
if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True # ✅ 自动重连
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency for FastAPI
def get_db():
    """Get database session as FastAPI dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database connection and create tables"""
    try:
        # Import all models to ensure they are registered with Base
        from app.models import database  # This imports all models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logging.info("Database connection initialized and tables created successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logging.info("Database connection closed")
