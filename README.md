# Superstar AI - "我是大明星"

**版本**: 2.0.0  
**状态**: 开发中

## 项目概述

Superstar AI 是一个商业化的 AI 图像生成平台，支持用户上传人脸照片并生成各种风格的个人写真。系统采用 FastAPI + PostgreSQL + Redis + Celery 架构，提供高性能、可扩展的图像生成服务。

### 核心功能

- ✅ **用户认证系统**：支持邮箱注册和认证
- ✅ **统一账户钱包**：积分系统
- ✅ **动态套餐系统**：管理员可配置的模板和定价
- ✅ **AI 图像生成**：基于火山引擎的图像生成服务
- ✅ **社区画廊**：公开展示用户作品，支持点赞、分享
- ✅ **异步任务处理**：Celery 异步处理长时间运行的生成任务
- ✅ **Redis 缓存**：高性能缓存层，优化频繁访问的数据

## 快速开始

### 本地开发环境

```bash
# 1. 克隆仓库
git clone <repository-url>
cd superstar_workspace

# 2. 使用 Docker Compose 启动服务
docker-compose up -d

# 3. 访问应用
# - API 文档: http://localhost:8000/docs
# - 前端界面: http://localhost:3000
# - 健康检查: http://localhost:8000/health
```

### 手动启动（不使用Docker）

```bash
# 1. 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 2. 设置环境变量
cp .env.example .env
# 编辑 .env 文件，填入数据库连接等配置

# 3. 启动后端服务
uvicorn app.main:app --reload --port 8000
```

## 技术栈

### 后端

- **框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL 14 (asyncpg)
- **缓存**: Redis 7
- **任务队列**: Celery 5.3.4
- **ORM**: SQLAlchemy 2.0.23 (异步)
- **迁移工具**: Alembic 1.13.0
- **认证**: JWT (python-jose)
- **图像处理**: Pillow 10.1.0

### 前端

- **框架**: Vue 3
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios

### 基础设施

- **容器化**: Docker + Docker Compose
- **AI 服务**: 火山引擎 (图像生成)

## 项目结构

```
superstar_workspace/
├── backend/                 # 后端代码
│   ├── app/                # 应用代码
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置和工具
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑层
│   │   └── middleware/     # 中间件
│   ├── requirements.txt    # 依赖文件
│   └── Dockerfile          # Docker 配置
├── frontend/               # 前端代码
│   ├── index.html          # 主页面
│   └── Dockerfile          # Docker 配置
├── docker-compose.yml      # Docker Compose 配置
└── README.md              # 项目文档
```

## API 接口

完整的 API 文档可通过以下方式访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 数据库迁移

```bash
# 进入后端目录
cd backend

# 创建新迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 开发指南

### 代码结构

```
backend/
├── app/
│   ├── api/v1/          # API 路由
│   ├── core/            # 核心配置和工具
│   ├── models/          # 数据模型（SQLAlchemy + Pydantic）
│   ├── schemas/         # Pydantic 模型定义
│   ├── services/        # 业务逻辑层
│   ├── middleware/      # 中间件
│   └── utils/           # 工具函数
```

### 开发流程

1. **创建功能分支**: `git checkout -b feature/your-feature`
2. **开发代码**: 遵循现有代码风格
3. **编写测试**: 添加单元测试和集成测试
4. **数据库迁移**: 如有数据库变更，创建 Alembic 迁移
5. **提交代码**: `git commit -m "feat: your feature"`
6. **创建 PR**: 提交 Pull Request 进行代码审查

## 部署指南

### 环境要求

- **服务器**: 2核4GB RAM 或更高
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 7+
- **存储**: 腾讯云 COS（推荐）

### 部署步骤

使用 Docker Compose 进行部署：

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入生产环境配置

# 2. 启动生产环境
docker-compose -f docker-compose.prod.yml up -d
```

## 故障排除

常见问题：

1. **依赖安装失败**: 确保 Python 版本为 3.8+，并使用虚拟环境
2. **数据库连接失败**: 检查数据库连接字符串和网络连接
3. **API 文档无法访问**: 确保服务已正确启动

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

私有项目 - 内部使用

---

**最后更新**: 2025-01-04  
**文档版本**: 2.0