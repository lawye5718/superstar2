# Superstar AI - 核心代码模块说明文档

## 1. 概述

本文档详细介绍了Superstar AI项目的核心代码模块，包括每个模块的功能、实现方式、关键代码片段以及模块间的交互关系。

## 2. 后端核心模块

### 2.1 app/main.py - 应用入口

**功能**: FastAPI应用的主入口点，负责应用初始化和中间件配置

**关键特性**:
- 应用生命周期管理
- CORS配置
- 中间件注册
- 路由注册
- 静态文件服务

**代码结构**:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api.v1.router import api_router
from scripts.init_data import init_db_data

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_db()
    init_db_data()
    yield
    # 关闭时
    await close_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# 注册中间件
app.add_middleware(CORSMiddleware, ...)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
```

**生命周期事件**:
- `lifespan`函数管理应用启动和关闭
- 启动时初始化数据库和示例数据
- 关闭时清理数据库连接

### 2.2 app/core/config.py - 配置管理

**功能**: 应用配置管理，使用Pydantic Settings进行环境变量管理

**关键特性**:
- 环境变量自动加载
- 类型验证
- 配置缓存

**代码结构**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置类"""
    # 应用配置
    APP_NAME: str = "Superstar AI"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./superstar.db"
    DATABASE_SYNC_URL: str = "sqlite:///./superstar.db"
    
    # 认证配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"

def get_settings():
    """获取配置实例"""
    return Settings()

settings = get_settings()
```

### 2.3 app/core/database.py - 数据库管理

**功能**: 数据库连接管理，支持异步和同步连接

**关键特性**:
- 异步数据库连接池
- 同步数据库连接
- 依赖注入函数

**代码结构**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 异步引擎和会话
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 同步引擎和会话
sync_engine = create_engine(settings.DATABASE_SYNC_URL)
SyncSessionLocal = sessionmaker(sync_engine, autocommit=False, autoflush=False)

async def get_async_db():
    """异步数据库依赖"""
    async with AsyncSessionLocal() as session:
        yield session

def get_sync_db():
    """同步数据库依赖"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2.4 app/core/security.py - 安全模块

**功能**: 认证和安全相关功能，包括密码加密和JWT令牌处理

**关键特性**:
- 密码哈希处理
- JWT令牌生成和验证
- 密码验证

**代码结构**:
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
```

### 2.5 app/core/dependencies.py - 依赖注入

**功能**: FastAPI依赖注入，处理认证和数据库连接

**关键特性**:
- 用户认证依赖
- 数据库连接依赖
- 权限验证

**代码结构**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.models.database import User

security_scheme = HTTPBearer()

async def get_current_user_id(
    token: str = Depends(security_scheme)
) -> str:
    """获取当前用户ID"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token.credentials, credentials_exception)

def get_current_active_user(
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
) -> User:
    """获取当前活跃用户"""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
```

### 2.6 app/models/database.py - 数据模型

**功能**: SQLAlchemy数据模型定义

**关键特性**:
- 用户模型
- 模板模型
- 订单模型
- 关系定义

**代码结构**:
```python
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    face_image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    orders = relationship("Order", back_populates="user")
    templates = relationship("Template", back_populates="creator")

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    cover_image_url = Column(String, nullable=False)
    price = Column(Float, default=9.9)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    prompt_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    creator = relationship("User", back_populates="templates")
    orders = relationship("Order", back_populates="template")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    amount = Column(Float, nullable=False)
    result_image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="orders")
    template = relationship("Template", back_populates="orders")
```

### 2.7 app/schemas/ - 数据传输对象

**功能**: Pydantic模型定义，用于数据验证和序列化

**关键模块**:

#### 2.7.1 app/schemas/user.py - 用户相关Schema
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    balance: Optional[float] = None

class User(UserBase):
    id: str
    balance: float
    is_active: bool
    is_superuser: bool
    face_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### 2.7.2 app/schemas/template.py - 模板相关Schema
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TemplateBase(BaseModel):
    title: str
    category: str
    cover_image_url: str
    price: float = 9.9

class TemplateCreate(TemplateBase):
    prompt_config: Optional[Dict[str, Any]] = {}

class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    cover_image_url: Optional[str] = None
    price: Optional[float] = None

class Template(TemplateBase):
    id: str
    usage_count: int
    is_active: bool
    prompt_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 2.8 app/services/ - 业务逻辑服务

**功能**: 封装业务逻辑，协调数据访问和外部服务

#### 2.8.1 app/services/user.py - 用户服务
```python
from sqlalchemy.orm import Session
from app.models.database import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserService:
    def __init__(self):
        pass
    
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """创建用户"""
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user_by_email(self, db: Session, email: str) -> User:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    def update_balance(self, db: Session, user_id: str, amount: float) -> User:
        """更新用户余额"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.balance += amount
            db.commit()
            db.refresh(user)
        return user
```

#### 2.8.2 app/services/order.py - 订单服务
```python
from sqlalchemy.orm import Session
from app.models.database import Order, User, Template
from app.schemas.order import OrderCreate
from app.core.exceptions import InsufficientBalanceError

class OrderService:
    def __init__(self):
        pass
    
    def create_order(self, db: Session, order_in: OrderCreate, user_id: str) -> Order:
        """创建订单"""
        # 获取模板信息
        template = db.query(Template).filter(Template.id == order_in.template_id).first()
        if not template:
            raise ValueError("Template not found")
        
        # 检查余额
        user = db.query(User).filter(User.id == user_id).first()
        if user.balance < template.price:
            raise InsufficientBalanceError()
        
        # 创建订单
        db_order = Order(
            user_id=user_id,
            template_id=order_in.template_id,
            amount=template.price,
            status="PENDING"
        )
        
        # 扣除余额
        user.balance -= template.price
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def update_order_status(self, db: Session, order_id: str, status: str, result_url: str = None) -> Order:
        """更新订单状态"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            if result_url:
                order.result_image_url = result_url
            db.commit()
            db.refresh(order)
        return order
```

### 2.9 app/api/v1/ - API路由

**功能**: 定义API端点，处理HTTP请求

#### 2.9.1 app/api/v1/users.py - 用户API
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_id, get_current_active_user
from app.core.database import get_sync_db
from app.models.database import User
from app.schemas.user import User as UserSchema, UserCreate
from app.services.user import UserService

router = APIRouter()
user_service = UserService()

@router.post("/", response_model=UserSchema)
def create_user(user_in: UserCreate, db: Session = Depends(get_sync_db)):
    """创建用户"""
    # 检查邮箱是否已存在
    existing_user = user_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建用户
    user = user_service.create_user(db, user_in)
    return user

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user
```

#### 2.9.2 app/api/v1/orders.py - 订单API
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_id, get_current_active_user
from app.core.database import get_sync_db
from app.models.database import Order, User
from app.schemas.order import OrderCreate, Order as OrderSchema
from app.services.order import OrderService

router = APIRouter()
order_service = OrderService()

@router.post("/", response_model=OrderSchema)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """创建订单"""
    try:
        order = order_service.create_order(db, order_in, current_user_id)
        # 触发异步任务
        from app.tasks.celery_app import generate_image_task
        generate_image_task.delay(order.id, order.template_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}", response_model=OrderSchema)
def read_order(
    order_id: str,
    db: Session = Depends(get_sync_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
```

### 2.10 app/tasks/celery_app.py - 异步任务

**功能**: Celery任务定义，处理耗时的AI生成任务

**代码结构**:
```python
from celery import Celery
from app.core.config import get_settings
from app.services.order import OrderService

settings = get_settings()

celery_app = Celery(
    "superstar",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.celery_app"]
)

@celery_app.task
def generate_image_task(order_id: str, template_id: str):
    """AI图像生成任务"""
    try:
        # 调用AI生成服务
        result = call_ai_generation_service(template_id)
        
        # 更新订单状态
        from app.core.database import SyncSessionLocal
        db = SyncSessionLocal()
        try:
            order_service = OrderService()
            order_service.update_order_status(db, order_id, "COMPLETED", result.url)
        finally:
            db.close()
        
        return {"status": "success", "result_url": result.url}
    except Exception as e:
        # 更新订单状态为失败
        from app.core.database import SyncSessionLocal
        db = SyncSessionLocal()
        try:
            order_service = OrderService()
            order_service.update_order_status(db, order_id, "FAILED")
        finally:
            db.close()
        raise e
```

## 3. 前端核心模块

### 3.1 frontend/index.html - 前端应用

**功能**: Vue 3单页面应用，包含所有前端逻辑

**关键特性**:
- Vue 3 Composition API
- 响应式状态管理
- API调用封装
- 用户界面组件

**主要组件结构**:

#### 3.1.1 状态管理
```javascript
const {
  // 基础状态
  currentView, isLoggedIn, user, token,
  
  // 相机视图状态
  currentCameraPhoto, isLoading,
  
  // 画廊视图状态
  galleryTemplates, categories, activeCategory,
  
  // 订单状态
  processingOrder, myOrders,
  
  // 管理员状态
  adminTab, adminUserList, adminStats, newTemplate,
  adminSubmitting,
  
  // 模态框状态
  showAuthModal, showUserModal, authMode, authForm,
  activeModalTab
} = setup();
```

#### 3.1.2 API调用封装
```javascript
const API_BASE = 'http://localhost:8000/api/v1';

// 用户认证API
const authAPI = {
  login: (credentials) => axios.post(`${API_BASE}/auth/login/access-token`, credentials),
  register: (userData) => axios.post(`${API_BASE}/users/`, userData)
};

// 模板API
const templateAPI = {
  get: () => axios.get(`${API_BASE}/templates/`),
  getRandom: () => axios.get(`${API_BASE}/templates/random`),
  create: (template) => axios.post(`${API_BASE}/admin/templates/`, template)
};

// 订单API
const orderAPI = {
  create: (orderData) => axios.post(`${API_BASE}/orders/`, orderData),
  get: (id) => axios.get(`${API_BASE}/orders/${id}`),
  getAll: () => axios.get(`${API_BASE}/orders/`)
};
```

#### 3.1.3 业务逻辑函数
```javascript
// 创建订单
const createOrder = async (template) => {
  if (!confirm(`确认制作？消耗 ¥${template.price}`)) return;
  try {
    const res = await axios.post(`${API_BASE}/orders/`, { template_id: template.id });
    user.value.balance -= template.price;
    processingOrder.value = { ...res.data, template };
    pollOrder(res.data.id);
    pendingTemplate.value = null; 
  } catch(e) { 
    alert(e.response?.data?.detail || "下单失败"); 
  }
};

// 订单轮询
const pollOrder = async (id) => {
  const interval = setInterval(async () => {
    try {
      const res = await axios.get(`${API_BASE}/orders/${id}`);
      if (processingOrder.value && processingOrder.value.id === id) {
        processingOrder.value.status = res.data.status;
        if (res.data.status === 'COMPLETED') {
          processingOrder.value.result_image_url = res.data.result_image_url;
          clearInterval(interval);
          fetchOrders(); 
        } else if (res.data.status === 'FAILED') {
          clearInterval(interval);
        }
      } else {
        clearInterval(interval); 
      }
    } catch { clearInterval(interval); }
  }, 3000);
};
```

## 4. 配置和部署模块

### 4.1 docker-compose.yml - 容器编排

**功能**: 定义多服务容器编排

**服务构成**:
- backend: FastAPI应用服务
- redis: Redis缓存和消息队列
- worker: Celery工作进程
- frontend: 前端服务

**关键配置**:
```yaml
version: '3.8'

services:
  # 后端API服务
  backend:
    build: 
      context: ./backend
    container_name: superstar_backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app                # 代码热更新
      - ./data/static:/app/static     # 图片持久化
      - ./data/db:/app/db_data        # 数据库持久化
    environment:
      - DATABASE_URL=sqlite:///./db_data/superstar.db
      - REDIS_URL=redis://redis:6379/0
    command: sh -c "python scripts/init_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    depends_on:
      - redis

  # Redis服务
  redis:
    image: redis:alpine
    container_name: superstar_redis
    ports:
      - "6379:6379"

  # Celery工作进程
  worker:
    build: 
      context: ./backend
    container_name: superstar_worker
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=sqlite:///./db_data/superstar.db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - ./data/static:/app/static
    depends_on:
      - backend
      - redis
```

### 4.2 backend/requirements.txt - 依赖管理

**功能**: Python项目依赖管理

**关键依赖**:
- FastAPI: Web框架
- SQLAlchemy: ORM
- Celery: 任务队列
- Redis: 缓存和消息队列
- Pydantic: 数据验证
- Passlib: 密码哈希
- python-jose: JWT处理

## 5. 模块交互关系

### 5.1 后端模块交互

```
API层 (app/api/) 
    ↓ (依赖注入)
服务层 (app/services/) 
    ↓ (数据库操作)
数据访问层 (SQLAlchemy ORM)
    ↓ (数据库)
PostgreSQL/SQLite
```

### 5.2 前后端交互

```
前端Vue应用 
    ↔ (HTTP API调用)
后端FastAPI服务 
    ↔ (异步任务)
Celery + Redis 
    ↔ (AI服务调用)
外部AI生成服务
```

### 5.3 认证流程

```
用户登录
    ↓
前端发送凭据
    ↓
后端验证凭据
    ↓
生成JWT令牌
    ↓
返回令牌给前端
    ↓
后续请求携带令牌
    ↓
后端验证令牌
    ↓
授权访问受保护资源
```

## 6. 关键业务流程

### 6.1 用户生成流程

1. 用户上传头像
2. 用户选择模板
3. 用户发起生成请求
4. 系统检查余额
5. 扣除费用并创建订单
6. 将生成任务加入队列
7. 异步处理AI生成
8. 更新订单状态
9. 用户查看结果

### 6.2 管理员操作流程

1. 管理员登录
2. 访问管理后台
3. 管理模板（上传/删除）
4. 查看用户列表
5. 查看运营数据

### 6.3 文件上传流程

1. 前端选择文件
2. 通过API上传文件
3. 后端验证文件类型和大小
4. 保存到指定目录
5. 返回访问URL

---

此核心代码模块文档详细说明了Superstar AI项目的各个模块功能、实现方式和交互关系，为开发人员提供了深入理解项目架构的基础。