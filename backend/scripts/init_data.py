"""Initialize database with sample data for development"""

import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings
from app.models.database import Base, Template, User, GenderEnum
from app.core.security import get_password_hash

settings = get_settings()

# 使用同步引擎，并添加 SQLite 的 check_same_thread 参数
engine_kwargs = {}
if settings.DATABASE_SYNC_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_SYNC_URL, echo=False, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db_data():
    """Initialize database with sample data"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        user_count = db.query(User).count()
        if user_count == 0:
            # 创建示例用户
            demo_user = User(
                id="test-user-uuid-001",
                email="demo@example.com",
                password_hash=get_password_hash("default_password"),
                balance=100,
                roles=["user"]
            )
            db.add(demo_user)
            db.commit()
            print("Created demo user")
        
        # 检查模板数据
        template_count = db.query(Template).count()
        if template_count == 0:
            # 创建示例模板
            templates_data = [
                {
                    "title": "军绿色毛呢大衣复古写真",
                    "gender": GenderEnum.FEMALE,
                    "tags": ["复古", "大衣", "冬季"],
                    "config": {
                        "base_prompt": "High quality, 8k resolution, masterpiece",
                        "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
                        "negative_prompt": "bad anatomy"
                    },
                    "is_approved": True,
                    "display_image_urls": ["https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=500&q=80"],
                    "price": 9.9,
                    "usage_count": 1250
                },
                {
                    "title": "祖母绿缎面礼裙轻奢",
                    "gender": GenderEnum.FEMALE,
                    "tags": ["轻奢", "礼裙", "优雅"],
                    "config": {
                        "base_prompt": "High quality, 8k resolution, masterpiece",
                        "variable_prompt": "wearing sage green satin dress, luxury background",
                        "negative_prompt": "bad anatomy"
                    },
                    "is_approved": True,
                    "display_image_urls": ["https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=500&q=80"],
                    "price": 19.9,
                    "usage_count": 890
                },
                {
                    "title": "网球风运动写真",
                    "gender": GenderEnum.FEMALE,
                    "tags": ["运动", "网球", "青春"],
                    "config": {
                        "base_prompt": "High quality, 8k resolution, masterpiece",
                        "variable_prompt": "wearing tennis outfit, sporty look",
                        "negative_prompt": "bad anatomy"
                    },
                    "is_approved": True,
                    "display_image_urls": ["https://images.unsplash.com/photo-1530915512336-367958254703?w=500&q=80"],
                    "price": 14.9,
                    "usage_count": 642
                },
                {
                    "title": "森系清新风格",
                    "gender": GenderEnum.FEMALE,
                    "tags": ["森系", "清新", "自然"],
                    "config": {
                        "base_prompt": "High quality, 8k resolution, masterpiece",
                        "variable_prompt": "in forest background, natural look",
                        "negative_prompt": "bad anatomy"
                    },
                    "is_approved": True,
                    "display_image_urls": ["https://images.unsplash.com/photo-1494790108755-2616b612b786?w=500&q=80"],
                    "price": 12.9,
                    "usage_count": 721
                },
                {
                    "title": "职场精英风",
                    "gender": GenderEnum.FEMALE,
                    "tags": ["职场", "精英", "商务"],
                    "config": {
                        "base_prompt": "High quality, 8k resolution, masterpiece",
                        "variable_prompt": "in business suit, professional look",
                        "negative_prompt": "bad anatomy"
                    },
                    "is_approved": True,
                    "display_image_urls": ["https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&q=80"],
                    "price": 16.9,
                    "usage_count": 583
                },
                {
                    "title": "海边度假风",
                    "gender": GenderEnum.FEMALE,
                    "tags": ["海边", "度假", "休闲"],
                    "config": {
                        "base_prompt": "High quality, 8k resolution, masterpiece",
                        "variable_prompt": "at beach, vacation style",
                        "negative_prompt": "bad anatomy"
                    },
                    "is_approved": True,
                    "display_image_urls": ["https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=500&q=80"],
                    "price": 18.9,
                    "usage_count": 432
                }
            ]
            
            for template_data in templates_data:
                template = Template(
                    title=template_data["title"],
                    gender=template_data["gender"],
                    tags=template_data["tags"],
                    config=template_data["config"],
                    is_approved=template_data["is_approved"],
                    display_image_urls=template_data["display_image_urls"],
                    price=template_data["price"],
                    usage_count=template_data["usage_count"]
                )
                db.add(template)
            
            db.commit()
            print(f"Created {len(templates_data)} sample templates")
        
        print("Database initialization completed!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db_data()