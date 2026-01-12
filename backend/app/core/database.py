from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from app.core.config import settings

connect_args = {}
if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True # 保持连接活跃
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_sync_db() -> Generator:
    """
    Dependency for getting sync database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator:
    """
    Alias for get_sync_db for backward compatibility.
    Note: If async DB is needed, use AsyncSession instead.
    """
    return get_sync_db()
