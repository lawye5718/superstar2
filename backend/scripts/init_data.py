"""Initialize database with sample data for development"""

import asyncio
import logging
import os
import sys

# 将 backend 加入 python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import User
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # 0. 确保表结构存在
    Base.metadata.create_all(bind=engine)

    # 1. 创建超级管理员
    admin_email = "admin@superstar.ai"
    user = db.query(User).filter(User.email == admin_email).first()
    if not user:
        logger.info(f"Creating superuser: {admin_email}")
        user = User(
            email=admin_email,
            username="SuperAdmin",
            hashed_password=get_password_hash("admin123"),
            balance=999999.0,
            is_active=True,
            is_superuser=True, # ✅ 关键权限
        )
        db.add(user)
        db.commit()
    else:
        logger.info("Superuser already exists.")

if __name__ == "__main__":
    logger.info("Initializing database...")
    db = SessionLocal()
    init_db(db)
    logger.info("Database initialization completed.")
