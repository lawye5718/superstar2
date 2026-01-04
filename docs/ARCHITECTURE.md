# Superstar AI 系统架构文档

## 1. 项目概述

Superstar AI 是一个商业化的 AI 图像生成平台，支持用户上传人脸照片并生成各种风格的个人写真。系统采用 FastAPI + PostgreSQL + Redis + Celery 架构，提供高性能、可扩展的图像生成服务。

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────┐
│   前端 (Vue 3)  │
│  Tailwind CSS   │
└────────┬────────┘
         │ HTTP/HTTPS
┌────────▼─────────────────────────────────────┐
│           FastAPI Backend                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   API    │  │  Cache   │  │  Auth    │ │
│  │  Routes  │  │ (Redis)  │  │   JWT    │ │
│  └────┬─────┘  └──────────┘  └──────────┘ │
│       │                                     │
│  ┌────▼──────────────────────────────────┐ │
│  │        Service Layer                   │ │
│  │  User / Template / Order / Gallery   │ │
│  └────┬──────────────────────────────────┘ │
│       │                                     │
│  ┌────▼──────────────────────────────────┐ │
│  │      Repository Layer                 │ │
│  │      (Database Access)                │ │
│  └────┬──────────────────────────────────┘ │
└───────┼─────────────────────────────────────┘
        │
┌───────▼──────────┐  ┌──────────────┐  ┌──────────────┐
│   PostgreSQL     │  │    Redis     │  │    Celery    │
│   (Database)     │  │   (Cache)    │  │  (Workers)   │
└──────────────────┘  └──────────────┘  └──────┬───────┘
                                                │
                                    ┌───────────▼───────────┐
                                    │  External Services   │
                                    │  - Volcano Engine    │
                                    │  - Tencent COS       │
                                    │  - Payment Gateways │
                                    └───────────────────────┘
```

### 2.2 关键设计原则

1. **分层架构**: API → Service → Repository → Database
2. **异步处理**: 长时间任务通过 Celery 异步处理
3. **缓存优先**: 频繁访问的数据使用 Redis 缓存
4. **依赖注入**: 使用 FastAPI 的依赖注入系统
5. **类型安全**: 使用 Pydantic 进行数据验证

## 3. 技术栈

### 3.1 后端技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL 14 (asyncpg)
- **缓存**: Redis 7
- **任务队列**: Celery 5.3.4
- **ORM**: SQLAlchemy 2.0.23 (异步)
- **迁移工具**: Alembic 1.13.0
- **认证**: JWT (python-jose)
- **图像处理**: Pillow 10.1.0

### 3.2 前端技术栈

- **构建工具**: CDN (Vue 3, Tailwind CSS, Axios)
- **框架**: Vue 3 (ES6 Modules)
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios

### 3.3 基础设施

- **容器化**: Docker + Docker Compose
- **云存储**: 腾讯云 COS
- **CDN**: 可配置的 CDN 域名
- **AI 服务**: 火山引擎 (图像生成)

## 4. 代码结构

### 4.1 后端目录结构

```
backend/
├── app/
│   ├── api/v1/          # API 路由
│   │   ├── __init__.py
│   │   ├── router.py    # 主路由
│   │   ├── users.py     # 用户路由
│   │   ├── templates.py # 模板路由
│   │   ├── orders.py    # 订单路由
│   │   ├── galleries.py # 画廊路由
│   │   └── tasks.py     # 任务路由
│   ├── core/            # 核心配置和工具
│   │   ├── __init__.py
│   │   ├── config.py    # 配置管理
│   │   ├── database.py  # 数据库配置
│   │   ├── security.py  # 安全工具
│   │   └── exceptions.py # 自定义异常
│   ├── models/          # 数据模型
│   │   ├── __init__.py
│   │   └── database.py  # SQLAlchemy 模型
│   ├── schemas/         # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py      # 用户模型
│   │   ├── template.py  # 模板模型
│   │   ├── order.py     # 订单模型
│   │   ├── gallery.py   # 画廊模型
│   │   └── task.py      # 任务模型
│   ├── services/        # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py      # 用户服务
│   │   ├── template_service.py  # 模板服务
│   │   ├── order_service.py     # 订单服务
│   │   ├── gallery_service.py   # 画廊服务
│   │   └── task_service.py      # 任务服务
│   ├── middleware/      # 中间件
│   │   ├── __init__.py
│   │   ├── error_handler.py # 错误处理中间件
│   │   └── logging.py       # 日志中间件
│   └── main.py          # 应用入口
├── requirements.txt     # 依赖文件
├── Dockerfile           # Docker 配置
└── alembic/             # 数据库迁移
    └── versions/
```

### 4.2 前端目录结构

```
frontend/
├── index.html           # 主页面
├── src/                 # 源代码
│   ├── components/      # Vue 组件
│   ├── services/        # API 服务
│   └── utils/           # 工具函数
├── assets/              # 静态资源
│   ├── images/
│   ├── css/
│   └── js/
├── public/              # 公共资源
└── Dockerfile           # Docker 配置
```

## 5. 数据库设计

### 5.1 数据模型关系

```
Users (1) ────── (M) Orders
   │                    │
   │                    └── (1) Package
   │
   │ (M) ────── UserGallery (M) ────── Templates
   │                    │
   │                    └── (M) Likes (M) ────── Users
   │
   │ (M) ────── GenerationTasks
```

### 5.2 核心表结构

#### users 表
- id: UUID (主键)
- email: String (唯一索引)
- phone: String (唯一索引，可选)
- password_hash: String
- wx_unionid: String (微信联合ID，唯一索引，可选)
- wx_openid: String (微信OpenID，索引，可选)
- apple_id: String (苹果ID，唯一索引，可选)
- credits: Integer (积分，默认0)
- roles: JSON (角色数组，默认["user"])
- created_at: DateTime
- updated_at: DateTime

#### prompts (templates) 表
- id: UUID (主键)
- title: String
- gender: Enum (Male, Female, Couple, Unisex)
- tags: JSON (标签数组)
- config: JSONB (模板配置)
- is_approved: Boolean (是否审核通过)
- display_image_urls: JSON (展示图片URL数组)
- created_at: DateTime
- updated_at: DateTime

#### packages 表
- id: UUID (主键)
- name: String
- description: Text (可选)
- item_count: Integer (包含生成次数)
- price: Numeric (价格)
- default_display_image_url: String (可选)
- is_active: Boolean (是否激活)
- created_at: DateTime
- updated_at: DateTime

#### generation_tasks 表
- id: UUID (主键)
- user_id: UUID (外键，索引)
- template_id: UUID (外键)
- status: Enum (PENDING, PROCESSING, COMPLETED, FAILED)
- portrait_url: String (肖像URL，可选)
- result_gallery_id: UUID (外键，可选)
- error_message: Text (错误信息，可选)
- created_at: DateTime
- updated_at: DateTime

## 6. API 设计

### 6.1 API 版本控制

所有 API 都通过 `/api/v1/` 前缀进行版本控制，便于未来扩展。

### 6.2 认证机制

使用 JWT Token 进行用户认证，通过 Authorization Header 传递。

### 6.3 API 端点

#### 用户相关
- `POST /api/v1/users/` - 创建用户
- `GET /api/v1/users/{user_id}` - 获取用户信息
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `DELETE /api/v1/users/{user_id}` - 删除用户

#### 模板相关
- `POST /api/v1/templates/` - 创建模板
- `GET /api/v1/templates/` - 获取模板列表
- `GET /api/v1/templates/{template_id}` - 获取模板详情
- `PUT /api/v1/templates/{template_id}` - 更新模板
- `DELETE /api/v1/templates/{template_id}` - 删除模板

#### 订单相关
- `POST /api/v1/orders/` - 创建订单
- `GET /api/v1/orders/` - 获取订单列表
- `GET /api/v1/orders/{order_id}` - 获取订单详情

#### 画廊相关
- `POST /api/v1/galleries/` - 创建画廊项目
- `GET /api/v1/galleries/` - 获取画廊列表

#### 任务相关
- `POST /api/v1/tasks/` - 创建生成任务
- `GET /api/v1/tasks/` - 获取任务列表
- `GET /api/v1/tasks/{task_id}` - 获取任务详情
- `PUT /api/v1/tasks/{task_id}` - 更新任务

## 7. 安全性

### 7.1 认证和授权

- 使用 JWT 进行用户认证
- 密码使用 bcrypt 哈希算法存储
- 支持第三方登录（微信、苹果ID）

### 7.2 输入验证

- 使用 Pydantic 进行请求数据验证
- SQL 注入防护（通过 ORM）
- XSS 防护（输出转义）

### 7.3 数据保护

- 敏感数据加密存储
- 访问日志记录
- 审计日志功能

## 8. 性能优化

### 8.1 数据库优化

- 适当的索引策略
- 连接池管理
- 查询优化

### 8.2 缓存策略

- Redis 缓存热门数据
- CDN 加速图片分发
- 响应压缩

### 8.3 异步处理

- 长时间任务使用 Celery 处理
- 非阻塞 I/O 操作
- 任务队列管理

## 9. 部署架构

### 9.1 容器化部署

使用 Docker 和 Docker Compose 进行容器化部署：

- backend: FastAPI 应用
- db: PostgreSQL 数据库
- redis: Redis 缓存
- frontend: Nginx 静态文件服务

### 9.2 生产环境配置

- 反向代理（Nginx）
- 负载均衡
- 监控和日志
- 自动化部署

## 10. 开发流程

### 10.1 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用类型注解
- 适当的文档字符串

### 10.2 测试策略

- 单元测试
- 集成测试
- API 测试

### 10.3 CI/CD

- 自动化测试
- 代码质量检查
- 自动化部署

## 11. 监控和维护

### 11.1 日志管理

- 结构化日志
- 日志级别控制
- 日志轮转

### 11.2 性能监控

- 响应时间监控
- 错误率监控
- 资源使用监控

### 11.3 健康检查

- 应用健康检查端点
- 数据库连接检查
- 外部服务可用性检查

---
**文档版本**: 1.0  
**最后更新**: 2025-01-04