"""SQLAlchemy database models"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from enum import Enum as PyEnum

from app.core.database import Base
from app.core.config import settings

# Use JSONB for PostgreSQL, JSON for SQLite
def get_json_type():
    """Return appropriate JSON type based on database"""
    if "postgresql" in settings.DATABASE_URL:
        return JSONB
    return JSON

JSONType = get_json_type()

# Use UUID for PostgreSQL, String for SQLite  
def get_uuid_type(as_uuid=False):
    """Return appropriate UUID type based on database"""
    if "postgresql" in settings.DATABASE_URL:
        return PostgresUUID(as_uuid=as_uuid)
    else:
        # SQLite doesn't have UUID type, use String instead
        return String(36)


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


class GenderEnum(PyEnum):
    """Gender enum"""
    MALE = "Male"
    FEMALE = "Female"
    COUPLE = "Couple"
    UNISEX = "Unisex"


class TaskStatusEnum(PyEnum):
    """Generation task status enum"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class OrderStatusEnum(PyEnum):
    """Order status enum"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PackageRuleTypeEnum(PyEnum):
    """Package template rule type enum"""
    FIXED = "FIXED"              # 固定模板列表
    RANDOM_TAG = "RANDOM_TAG"    # 随机标签
    RANDOM_SET = "RANDOM_SET"    # 随机集合（如"本周热门"）
    RANDOM_ALL = "RANDOM_ALL"    # 完全随机


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Third-party authentication
    wx_unionid = Column(String(100), unique=True, nullable=True, index=True)
    wx_openid = Column(String(100), nullable=True, index=True)
    apple_id = Column(String(100), unique=True, nullable=True, index=True)
    
    # Credits (wallet)
    credits = Column(Numeric(10, 2), default=0, nullable=False)
    
    # User profile
    face_image_url = Column(String(500), nullable=True)  # User uploaded face image
    gender = Column(String(20), nullable=True)  # User gender
    
    # Roles (array stored as JSON)
    roles = Column(JSON, default=lambda: ["user"], nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    galleries = relationship("UserGallery", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    generation_tasks = relationship("GenerationTask", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("TemplateFavorite", back_populates="user", cascade="all, delete-orphan")

    @property
    def balance(self):
        """Alias for credits to keep API naming consistent"""
        return float(self.credits or 0)


class Template(Base):
    """Template (Prompt) model"""
    __tablename__ = "prompts"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    gender = Column(SQLEnum(GenderEnum), nullable=False, index=True)
    tags = Column(JSON, default=lambda: [], nullable=False, index=True)  # Array of strings
    
    # Template configuration (V14 format stored as JSON/JSONB)
    config = Column(JSONType, nullable=False)
    
    # Approval status
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    
    # Display images for waiting screen
    display_image_urls = Column(JSON, default=lambda: [], nullable=False)  # Array of URLs
    
    # Pricing and usage
    price = Column(Numeric(10, 2), default=9.9, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    galleries = relationship("UserGallery", back_populates="template")
    package_rules = relationship("PackageTemplateRule", back_populates="prompt")
    favorites = relationship("TemplateFavorite", back_populates="template")


class Package(Base):
    """Package model"""
    __tablename__ = "packages"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    item_count = Column(Integer, nullable=False)  # Number of generations
    price = Column(Numeric(10, 2), nullable=False)
    default_display_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    rules = relationship("PackageTemplateRule", back_populates="package", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="package")


class PackageTemplateRule(Base):
    """Package template rule model"""
    __tablename__ = "package_template_rules"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    package_id = Column(get_uuid_type(as_uuid=False), ForeignKey("packages.id"), nullable=False, index=True)
    rule_type = Column(SQLEnum(PackageRuleTypeEnum), nullable=False)
    rule_config = Column(JSONType, nullable=False)  # e.g., {"tag": "古风"} or {"template_ids": ["uuid1", "uuid2"]}
    
    # Optional: link to specific template (for FIXED type)
    template_id = Column(get_uuid_type(as_uuid=False), ForeignKey("prompts.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    package = relationship("Package", back_populates="rules")
    prompt = relationship("Template", back_populates="package_rules")


class GenerationTask(Base):
    """Generation task model (for async processing)"""
    __tablename__ = "generation_tasks"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(get_uuid_type(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    template_id = Column(get_uuid_type(as_uuid=False), ForeignKey("prompts.id"), nullable=False)
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.PENDING, nullable=False, index=True)
    
    # V15.1: Portrait URL for generation
    portrait_url = Column(String(500), nullable=True)
    
    # Result
    result_gallery_id = Column(get_uuid_type(as_uuid=False), ForeignKey("user_galleries.id"), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="generation_tasks")
    result_gallery = relationship("UserGallery", foreign_keys=[result_gallery_id])


class UserGallery(Base):
    """User gallery model"""
    __tablename__ = "user_galleries"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(get_uuid_type(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    template_id = Column(get_uuid_type(as_uuid=False), ForeignKey("prompts.id"), nullable=False, index=True)
    
    # Image URLs
    image_url_free = Column(String(500), nullable=False)  # 1080p with watermark
    image_url_paid = Column(String(500), nullable=True)   # 4K without watermark
    thumbnail_url = Column(String(500), nullable=True)     # 256x256 thumbnail
    
    # Public gallery
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="galleries")
    template = relationship("Template", back_populates="galleries")
    likes = relationship("Like", back_populates="gallery_item", cascade="all, delete-orphan")


class Like(Base):
    """Like model (for public gallery)"""
    __tablename__ = "likes"
    
    user_id = Column(get_uuid_type(as_uuid=False), ForeignKey("users.id"), primary_key=True)
    gallery_item_id = Column(get_uuid_type(as_uuid=False), ForeignKey("user_galleries.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    gallery_item = relationship("UserGallery", back_populates="likes")


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(get_uuid_type(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    package_id = Column(get_uuid_type(as_uuid=False), ForeignKey("packages.id"), nullable=True)
    template_id = Column(get_uuid_type(as_uuid=False), ForeignKey("prompts.id"), nullable=True)  # 添加模板ID
    credits_purchased = Column(Integer, nullable=False)  # Credits added to user account
    credits_consumed = Column(Numeric(10, 2), default=0, nullable=False)  # 消耗积分
    
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False, index=True)
    
    # Platform
    platform = Column(String(20), nullable=False, index=True)  # 'web', 'wx_mini'
    
    # Transaction ID from payment gateway
    transaction_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Result image URL
    result_image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    package = relationship("Package", back_populates="orders")


class AuditLog(Base):
    """Audit log model (V14 compatibility)"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    actor_user_id = Column(get_uuid_type(as_uuid=False), ForeignKey("users.id"), nullable=True)
    action_type = Column(String(100), nullable=False, index=True)
    details = Column(JSONType, nullable=True)


class TemplateFavorite(Base):
    """User template favorites model"""
    __tablename__ = "template_favorites"
    
    id = Column(get_uuid_type(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(get_uuid_type(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    template_id = Column(get_uuid_type(as_uuid=False), ForeignKey("prompts.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    template = relationship("Template", back_populates="favorites")
    
    # Unique constraint: one user can only favorite a template once
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class SystemSetting(Base):
    """System settings model (V14 compatibility)"""
    __tablename__ = "system_settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSONType, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
