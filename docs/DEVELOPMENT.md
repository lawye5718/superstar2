# Superstar AI 开发指南

## 1. 项目概述

### 1.1 项目结构

```
superstar2/
├── backend/                  # 后端代码
│   ├── app/                 # 应用代码
│   │   ├── api/            # API路由
│   │   │   └── v1/         # API版本1
│   │   │       ├── admin/  # 管理员API
│   │   │       └── ...     # 其他API
│   │   ├── core/           # 核心组件
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── scripts/            # 初始化脚本
│   ├── static/             # 静态文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── index.html          # 主页面
│   └── assets/             # 静态资源
├── docs/                   # 文档
├── tests/                  # 测试文件
├── docker-compose.yml      # Docker编排配置
└── .env.example            # 环境变量示例
```

### 1.2 技术栈

- **后端**: FastAPI + SQLAlchemy + Celery + Redis
- **前端**: Vue.js 3 + Tailwind CSS
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **消息队列**: Redis + Celery
- **部署**: Docker + Docker Compose

## 2. 开发环境设置

### 2.1 环境要求

- Python 3.8+ (推荐 3.11 或 3.12)
- Node.js 16+ (用于前端开发)
- Docker & Docker Compose
- Git

### 2.2 本地开发环境搭建

#### 2.2.1 后端环境

1. **克隆项目**
   ```bash
   git clone https://github.com/lawye5718/superstar2.git
   cd superstar2
   ```

2. **创建虚拟环境**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，根据需要修改配置
   ```

5. **启动后端服务**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### 2.2.2 前端环境

前端使用纯HTML + Vue.js，无需额外构建工具。

1. **启动前端服务**（开发模式）
   ```bash
   # 使用Python内置服务器
   cd frontend
   python -m http.server 8080
   
   # 或使用Node.js服务器
   npx serve .
   
   # 或使用Docker
   docker run -it --rm -p 8080:80 -v $(pwd)/frontend:/usr/share/nginx/html nginx
   ```

#### 2.2.3 Docker开发环境

```bash
# 启动所有服务（开发模式）
docker-compose up --build

# 或只启动后端和依赖
docker-compose up backend redis worker
```

## 3. 代码规范

### 3.1 Python 代码规范

遵循 PEP 8 规范，使用以下工具：

- **格式化**: black
- **静态检查**: flake8, mypy
- **导入排序**: isort

```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8 .
mypy .
```

### 3.2 命名规范

- **变量/函数**: `snake_case`
- **类**: `PascalCase`
- **常量**: `UPPER_SNAKE_CASE`
- **私有成员**: `_private_member`

### 3.3 前端代码规范

- **HTML/CSS**: 遵循 BEM 命名规范
- **JavaScript**: 使用 ES6+ 语法
- **Vue.js**: 遵循 Composition API 模式

## 4. 数据库设计

### 4.1 数据模型

#### 4.1.1 User 模型
- `id`: UUID, 主键
- `email`: 字符串, 唯一
- `username`: 字符串
- `hashed_password`: 字符串
- `balance`: 浮点数, 默认0.0
- `is_active`: 布尔值, 默认True
- `is_superuser`: 布尔值, 默认False
- `face_image_url`: 字符串, 可空
- `gender`: 枚举, 可空
- `created_at`: 时间戳
- `updated_at`: 时间戳

#### 4.1.2 Template 模型
- `id`: UUID, 主键
- `title`: 字符串
- `category`: 字符串
- `cover_image_url`: 字符串
- `price`: 浮点数
- `usage_count`: 整数, 默认0
- `is_active`: 布尔值, 默认True
- `prompt_config`: JSON, 可空
- `created_at`: 时间戳
- `updated_at`: 时间戳

#### 4.1.3 Order 模型
- `id`: UUID, 主键
- `user_id`: UUID, 外键
- `template_id`: UUID, 外键
- `status`: 字符串 (PENDING, PROCESSING, COMPLETED, FAILED)
- `amount`: 浮点数
- `result_image_url`: 字符串, 可空
- `created_at`: 时间戳
- `updated_at`: 时间戳

### 4.2 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 创建迁移脚本
alembic revision --autogenerate -m "描述迁移内容"

# 应用迁移
alembic upgrade head

# 查看当前版本
alembic current
```

## 5. API 开发

### 5.1 API 设计原则

1. **RESTful 设计**
   - 使用名词而非动词
   - 使用 HTTP 方法表示操作
   - 使用嵌套表示关系

2. **版本控制**
   - API 版本通过 URL 路径控制 (`/api/v1/`)
   - 向后兼容

3. **错误处理**
   - 使用标准 HTTP 状态码
   - 统一错误响应格式

### 5.2 创建新 API 端点

#### 5.2.1 后端 API 端点

1. **定义 Schema** (`app/schemas/`)
   ```python
   from pydantic import BaseModel
   
   class NewResourceCreate(BaseModel):
       name: str
       description: str
   ```

2. **定义模型** (`app/models/`)
   ```python
   from sqlalchemy import Column, String, Integer
   from app.core.database import Base
   
   class NewResource(Base):
       __tablename__ = "new_resources"
       
       id = Column(String, primary_key=True)
       name = Column(String, nullable=False)
       description = Column(String)
   ```

3. **创建路由** (`app/api/v1/new_resource.py`)
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from app.core.database import get_sync_db
   from app.schemas.new_resource import NewResourceCreate
   from app.models import NewResource
   
   router = APIRouter()
   
   @router.post("/", response_model=NewResource)
   def create_new_resource(
       resource: NewResourceCreate,
       db: Session = Depends(get_sync_db)
   ):
       db_resource = NewResource(**resource.dict())
       db.add(db_resource)
       db.commit()
       db.refresh(db_resource)
       return db_resource
   ```

4. **注册路由** (`app/api/v1/router.py`)
   ```python
   from . import new_resource
   api_router.include_router(new_resource.router, prefix="/new_resources", tags=["new_resources"])
   ```

### 5.3 认证与授权

#### 5.3.1 JWT 认证

- 使用 `python-jose` 实现 JWT
- 令牌有效期：30分钟
- 刷新令牌：7天

#### 5.3.2 管理员权限

- `is_superuser` 字段控制管理员权限
- 所有管理员API需要验证管理员权限

## 6. 前端开发

### 6.1 前端架构

- **框架**: Vue.js 3 Composition API
- **样式**: Tailwind CSS
- **HTTP客户端**: Axios

### 6.2 组件结构

```html
<!-- 主应用组件结构 -->
<div id="app">
  <!-- 导航栏 -->
  <nav>...</nav>
  
  <!-- 主视图 -->
  <main>
    <!-- 未登录欢迎页 -->
    <!-- 复古相机视图 -->
    <!-- 画廊视图 -->
    <!-- 管理员后台 -->
  </main>
  
  <!-- 模态框 -->
  <div v-if="showAuthModal">...</div>
  <div v-if="showUserModal">...</div>
</div>
```

### 6.3 状态管理

使用 Vue 3 的响应式 API 进行状态管理：

```javascript
const {
  // 状态
  currentView, isLoggedIn, user, token,
  currentCameraPhoto, galleryTemplates, processingOrder,
  
  // UI状态
  showAuthModal, showUserModal, isLoading, isUploading,
  
  // 管理员数据
  adminTab, adminUserList, adminStats, newTemplate,
  
  // 方法
  handleAuth, logout, fetchUserInfo, createOrder,
  // ...
} = setup();
```

## 7. 测试策略

### 7.1 单元测试

使用 pytest 编写单元测试：

```python
# test_*.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

### 7.2 集成测试

测试整个API流程：

```python
def test_complete_order_flow():
    # 1. 创建用户
    user_response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    # 2. 登录获取token
    login_response = client.post("/api/v1/auth/login/access-token", 
                                data={
                                    "username": "test@example.com",
                                    "password": "password123"
                                })
    
    # 3. 创建订单
    token = login_response.json()["access_token"]
    order_response = client.post("/api/v1/orders/", 
                                headers={"Authorization": f"Bearer {token}"},
                                json={"template_id": "some-template-id"})
    
    assert order_response.status_code == 200
```

### 7.3 前端测试

前端测试使用浏览器自动化工具（如 Selenium）进行端到端测试。

## 8. 消息队列与异步任务

### 8.1 Celery 配置

- **Broker**: Redis
- **Backend**: Redis
- **任务**: 图像生成、文件处理等耗时操作

### 8.2 任务定义

```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "superstar",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task
def generate_image_task(order_id: str, template_id: str, user_image_path: str):
    """异步图像生成任务"""
    # 图像生成逻辑
    pass
```

### 8.3 任务调用

```python
# 在API中调用异步任务
from app.tasks.celery_app import generate_image_task

@router.post("/orders/")
def create_order(...):
    # 创建订单记录
    order = Order(...)
    db.add(order)
    db.commit()
    
    # 异步执行图像生成
    generate_image_task.delay(order.id, order.template_id, user_image_path)
    
    return order
```

## 9. 文件上传与存储

### 9.1 上传流程

1. 前端选择文件
2. 通过 `/utils/upload` API 上传
3. 后端验证文件类型和大小
4. 保存到静态目录
5. 返回访问URL

### 9.2 存储策略

- **开发环境**: 本地存储
- **生产环境**: 可配置为 COS、S3 或其他对象存储
- **文件类型**: 仅允许图像文件 (jpg, jpeg, png, webp, gif)
- **文件大小**: 限制 10MB

## 10. 管理员功能

### 10.1 管理员权限

- 创建/删除模板
- 查看用户列表
- 访问数据看板
- 管理系统配置

### 10.2 数据看板

实时显示运营数据：
- 总用户数
- 总收入
- 完成订单数
- 模板数量

## 11. 调试技巧

### 11.1 后端调试

1. **启用调试模式**
   ```python
   # 在 .env 中设置
   DEBUG=True
   ```

2. **日志记录**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Debug message")
   ```

3. **数据库查询调试**
   ```python
   # 启用SQLAlchemy日志
   import logging
   logging.basicConfig()
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

### 11.2 前端调试

1. **浏览器开发者工具**
   - Network 标签查看API请求
   - Console 查看错误信息
   - Elements 检查DOM结构

2. **Vue DevTools**
   - 安装 Vue DevTools 扩展
   - 检查组件状态和事件

## 12. 性能优化

### 12.1 数据库优化

1. **查询优化**
   - 使用索引
   - 避免 N+1 查询
   - 使用连接查询而非多次查询

2. **连接池**
   - 配置合适的连接池大小
   - 设置连接超时时间

### 12.2 缓存策略

1. **Redis 缓存**
   - 缓存热门模板
   - 缓存用户会话

2. **前端缓存**
   - 合理设置HTTP缓存头
   - 使用CDN加速静态资源

## 13. 安全考虑

### 13.1 输入验证

- 使用 Pydantic 进行数据验证
- 验证文件类型和大小
- 防止SQL注入

### 13.2 身份验证

- JWT令牌认证
- 密码哈希存储
- 会话管理

### 13.3 权限控制

- 管理员权限验证
- 用户数据隔离
- API速率限制

## 14. 部署前检查清单

### 14.1 代码检查

- [ ] 代码格式化 (black, isort)
- [ ] 静态分析 (flake8, mypy)
- [ ] 安全扫描 (bandit)
- [ ] 依赖更新

### 14.2 配置检查

- [ ] 环境变量配置正确
- [ ] 生产密钥已设置
- [ ] 数据库连接正常
- [ ] 外部服务API密钥配置

### 14.3 测试检查

- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] API端点功能正常
- [ ] 前端页面加载正常

## 15. 贡献指南

### 15.1 分支策略

- `main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 15.2 提交规范

使用约定式提交格式：

```
<type>(<scope>): <short summary>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 15.3 代码审查

提交PR前请确保：
- 代码符合规范
- 添加了适当的测试
- 更新了相关文档
- 解决了所有CI/CD检查问题