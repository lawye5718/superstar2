# Superstar AI - 代码架构与设计模式文档

## 1. 整体架构设计

### 1.1 架构模式

Superstar AI 采用**分层架构模式**（Layered Architecture），结合**领域驱动设计**（DDD）理念，主要包含以下几个层次：

```
┌─────────────────────────────────────────┐
│              表现层 (Presentation)        │
│         (API路由、HTTP处理)              │
├─────────────────────────────────────────┤
│              服务层 (Service)           │
│        (业务逻辑、事务管理)              │
├─────────────────────────────────────────┤
│              数据访问层 (Repository)      │
│        (数据库操作、ORM映射)              │
├─────────────────────────────────────────┤
│              数据模型层 (Model)          │
│         (实体定义、数据结构)              │
└─────────────────────────────────────────┘
```

### 1.2 设计原则

- **单一职责原则 (SRP)**: 每个类或函数只负责一个功能
- **开闭原则 (OCP)**: 对扩展开放，对修改关闭
- **依赖倒置原则 (DIP)**: 依赖于抽象而不是具体实现
- **接口隔离原则 (ISP)**: 使用小而专一的接口
- **里氏替换原则 (LSP)**: 子类型必须能够替换其基类型

## 2. 后端架构设计

### 2.1 分层架构详解

#### 2.1.1 API层 (app/api/)

**职责**:
- 处理HTTP请求和响应
- 参数验证和序列化
- 身份认证和权限检查
- 调用服务层处理业务逻辑

**实现模式**:
- 使用FastAPI的依赖注入系统
- Pydantic模型进行数据验证
- 统一的错误处理机制

**示例代码结构**:
```python
@router.post("/", response_model=schema.UserResponse)
def create_user(
    user_in: schema.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 权限检查
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 调用服务层
    user = user_service.create_user(db, user_in)
    
    # 返回响应
    return user
```

#### 2.1.2 服务层 (app/services/)

**职责**:
- 实现核心业务逻辑
- 协调多个数据访问操作
- 处理事务管理
- 业务规则验证

**设计模式**:
- **服务对象模式**: 将业务逻辑封装在服务类中
- **策略模式**: 不同业务场景使用不同策略
- **工厂模式**: 创建复杂对象

**示例代码结构**:
```python
class UserService:
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        # 业务逻辑验证
        if self.email_exists(db, user_in.email):
            raise ValueError("Email already registered")
        
        # 创建用户
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password)
        )
        
        # 保存到数据库
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def email_exists(self, db: Session, email: str) -> bool:
        return db.query(User).filter(User.email == email).first() is not None
```

#### 2.1.3 数据访问层 (Repository模式)

**职责**:
- 封装数据库操作
- 提供统一的数据访问接口
- 处理数据映射

**实现方式**:
- 使用SQLAlchemy ORM
- 实现Repository接口
- 支持查询构建器模式

**示例代码结构**:
```python
class UserRepository:
    def get_by_id(self, db: Session, id: str) -> User:
        return db.query(User).filter(User.id == id).first()
    
    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def update(self, db: Session, user: User) -> User:
        db.commit()
        db.refresh(user)
        return user
```

#### 2.1.4 数据模型层 (app/models/)

**职责**:
- 定义数据结构
- ORM映射配置
- 数据库表结构定义

**设计特点**:
- 使用SQLAlchemy ORM
- 支持关系映射
- 数据验证和约束

## 3. 核心设计模式

### 3.1 依赖注入模式 (Dependency Injection)

**应用场景**: 
- 数据库连接注入
- 认证依赖注入
- 服务依赖注入

**实现方式**:
```python
# FastAPI内置依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(
    token: str = Security(security_scheme)
) -> str:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    return security.verify_token(token, credentials_exception)
```

### 3.2 单例模式 (Singleton Pattern)

**应用场景**:
- 数据库连接池
- 配置管理器
- 日志记录器

**实现方式**:
```python
from functools import lru_cache

@lru_cache()
def get_settings():
    return Settings()
```

### 3.3 工厂模式 (Factory Pattern)

**应用场景**:
- 创建不同类型的用户
- 创建不同类型的模板
- 创建不同类型的订单

**实现方式**:
```python
class TemplateFactory:
    @staticmethod
    def create_template(template_type: str, **kwargs) -> Template:
        if template_type == "photo":
            return PhotoTemplate(**kwargs)
        elif template_type == "art":
            return ArtTemplate(**kwargs)
        else:
            raise ValueError(f"Unknown template type: {template_type}")
```

### 3.4 观察者模式 (Observer Pattern)

**应用场景**:
- 订单状态变化通知
- 用户积分变动通知
- 文件上传完成通知

**实现方式**:
```python
class EventManager:
    def __init__(self):
        self._observers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(callback)
    
    def notify(self, event_type, data):
        if event_type in self._observers:
            for callback in self._observers[event_type]:
                callback(data)
```

### 3.5 策略模式 (Strategy Pattern)

**应用场景**:
- 不同的支付策略
- 不同的文件存储策略
- 不同的AI生成策略

**实现方式**:
```python
from abc import ABC, abstractmethod

class StorageStrategy(ABC):
    @abstractmethod
    def save(self, file_path: str, content: bytes) -> str:
        pass

class LocalStorageStrategy(StorageStrategy):
    def save(self, file_path: str, content: bytes) -> str:
        # 本地存储逻辑
        pass

class COSStorageStrategy(StorageStrategy):
    def save(self, file_path: str, content: bytes) -> str:
        # 腾讯云COS存储逻辑
        pass
```

## 4. 前端架构设计

### 4.1 组件化架构

**Vue 3 Composition API**:
- 逻辑复用通过Composable函数
- 状态管理通过ref和reactive
- 组件通信通过props和emit

**组件结构**:
```
App.vue
├── Layout/
│   ├── Header.vue
│   ├── Sidebar.vue
│   └── Footer.vue
├── Pages/
│   ├── Home.vue
│   ├── Login.vue
│   ├── Gallery.vue
│   └── Admin.vue
└── Components/
    ├── UserCard.vue
    ├── TemplateCard.vue
    └── OrderCard.vue
```

### 4.2 状态管理

**响应式数据管理**:
```javascript
// 使用Vue 3 Composition API
const user = ref({ balance: 0, is_superuser: false })
const templates = ref([])
const orders = ref([])

// 计算属性
const availableTemplates = computed(() => {
    return templates.value.filter(t => t.price <= user.value.balance)
})
```

### 4.3 模块化设计

**API模块化**:
```javascript
// api.js - 统一API管理
const API = {
    auth: {
        login: (credentials) => axios.post('/auth/login', credentials),
        register: (userData) => axios.post('/users/', userData)
    },
    templates: {
        get: () => axios.get('/templates/'),
        create: (template) => axios.post('/admin/templates/', template),
        delete: (id) => axios.delete(`/admin/templates/${id}`)
    },
    orders: {
        create: (orderData) => axios.post('/orders/', orderData),
        get: (id) => axios.get(`/orders/${id}`)
    }
}
```

## 5. 异步处理架构

### 5.1 Celery任务队列

**架构模式**:
```
Web应用 → Redis → Celery Worker → AI服务
     ↑                              ↓
     └─── 结果存储 ←──────────────────┘
```

**任务定义**:
```python
@celery_app.task(bind=True)
def generate_image_task(self, order_id: str, template_id: str, user_image_path: str):
    try:
        # 调用AI生成服务
        result = ai_service.generate_image(template_id, user_image_path)
        
        # 更新订单状态
        order_service.update_order_status(order_id, 'COMPLETED', result_url=result.url)
        
        return {'status': 'success', 'result_url': result.url}
    except Exception as e:
        # 更新订单状态为失败
        order_service.update_order_status(order_id, 'FAILED')
        raise self.retry(exc=e, countdown=60, max_retries=3)
```

### 5.2 异步API设计

**WebSocket实时更新**:
```python
@router.websocket("/ws/orders/{order_id}")
async def websocket_order_updates(websocket: WebSocket, order_id: str):
    await websocket.accept()
    while True:
        order = order_service.get_order(db, order_id)
        await websocket.send_json({
            'status': order.status,
            'progress': order.progress
        })
        if order.status in ['COMPLETED', 'FAILED']:
            break
        await asyncio.sleep(2)
```

## 6. 安全架构

### 6.1 认证授权架构

**JWT Token流程**:
```
用户登录 → 验证凭据 → 生成JWT → 返回令牌 → 后续请求携带令牌 → 验证令牌 → 授权访问
```

**实现细节**:
```python
# 令牌生成
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 令牌验证
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
```

### 6.2 权限控制

**基于角色的访问控制 (RBAC)**:
```python
def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

## 7. 数据库设计模式

### 7.1 连接管理

**连接池配置**:
```python
# 数据库连接配置
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### 7.2 事务管理

**自动事务管理**:
```python
async def execute_in_transaction(func, *args, **kwargs):
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                result = await func(session, *args, **kwargs)
                await session.commit()
                return result
        except Exception:
            await session.rollback()
            raise
```

## 8. 错误处理架构

### 8.1 统一错误处理

**自定义异常**:
```python
class SuperstarException(Exception):
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class InsufficientBalanceError(SuperstarException):
    def __init__(self):
        super().__init__("Insufficient balance", "INSUFFICIENT_BALANCE")
```

**异常处理器**:
```python
@app.exception_handler(SuperstarException)
async def superstar_exception_handler(request: Request, exc: SuperstarException):
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )
```

## 9. 配置管理架构

### 9.1 环境配置

**配置分层**:
```python
class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Superstar AI"
    APP_VERSION: str = "2.0.0"
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    
    # 认证配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 外部服务配置
    VOLCANO_API_KEY: Optional[str] = None
    CDN_DOMAIN: Optional[str] = None
    
    class Config:
        env_file = ".env"
```

## 10. 扩展性设计

### 10.1 插件架构

**可扩展组件**:
- 存储策略（本地、COS、S3）
- 支付方式（支付宝、微信、银行卡）
- AI引擎（火山引擎、其他API）

### 10.2 微服务准备

**服务拆分准备**:
- 清晰的模块边界
- 统一的API接口
- 独立的数据库连接
- 消息队列通信

## 11. 性能优化策略

### 11.1 缓存策略

**多层缓存**:
- Redis缓存热点数据
- 浏览器缓存静态资源
- CDN加速图片分发

### 11.2 数据库优化

**查询优化**:
- 合理使用索引
- 避免N+1查询
- 批量操作优化

---

此架构设计文档详细说明了Superstar AI项目的代码架构和设计模式，为后续开发和维护提供了清晰的指导。