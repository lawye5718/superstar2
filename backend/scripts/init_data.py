import logging
import os
import sys

# 将 backend 加入 python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import User, Template
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # 0. 确保数据库表已创建
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
            is_superuser=True,
        )
        db.add(user)
        db.commit()
    else:
        logger.info("Superuser exists.")

    # 2. 创建演示模版
    if db.query(Template).count() == 0:
        logger.info("Creating demo template...")
        db.add(Template(
            title="复古·Classic",
            gender="Unisex",  # 使用GenderEnum中的值
            tags=["复古", "classic"],
            config={"base_prompt": "vintage film style", "variable_prompt": "coat", "negative_prompt": "blurry, low quality"},
            price=9.9,
            display_image_urls=["https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500&q=80"],
            is_approved=True
        ))
        db.commit()

if __name__ == "__main__":
    logger.info("Starting init...")
    db = SessionLocal()
    init_db(db)
    logger.info("Init completed.")
