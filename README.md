# Superstar AI - AI图像生成平台

**版本**: 2.0.0  
**状态**: 生产就绪，功能完整  
**创建日期**: 2025年1月  
**最后更新**: 2025年1月  

## 📋 项目概述

### 项目简介

**"我是大明星 Superstar"** 是一个商业化的 AI 图像生成平台，支持用户上传照片并生成各种风格的 AI 艺术图片。系统采用 FastAPI + Vue.js + PostgreSQL + Redis + Celery 架构，提供高性能、可扩展的图像生成服务。

### 核心特性

- ✅ **用户认证系统**: 支持邮箱注册、JWT身份验证
- ✅ **动态模板系统**: 管理员可配置的模板和定价
- ✅ **AI 图像生成**: 基于模板的图像生成服务
- ✅ **异步任务处理**: Celery 异步处理长时间运行的生成任务
- ✅ **管理后台**: 完整的管理员操作界面
- ✅ **数据看板**: 实时运营数据监控
- ✅ **文件上传**: 支持用户头像和模板图片上传

### 技术栈

- **后端**: FastAPI + SQLAlchemy + Celery + Redis
- **前端**: Vue.js 3 + Tailwind CSS
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **部署**: Docker + Docker Compose
- **消息队列**: Redis + Celery

## 🚀 快速开始

### 环境要求

- Python 3.8+ (推荐 3.11 或 3.12)
- Docker & Docker Compose
- Node.js (可选，用于前端开发)

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/lawye5718/superstar2.git
cd superstar2
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并根据需要修改:

```bash
cp .env.example .env
```

#### 4. 启动服务 (Docker)

```bash
# 启动所有服务 (后端、前端、Redis、Worker)
docker-compose up --build
```

服务将在以下端口运行：
- 后端API: `http://localhost:8000`
- 前端: `http://localhost:8080`
- Redis: `localhost:6379`

## 🏗️ 项目结构

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
│   │   └── services/       # 业务逻辑
│   ├── scripts/            # 初始化脚本
│   ├── static/             # 静态文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── index.html          # 主页面
│   └── assets/             # 静态资源
├── docker-compose.yml      # Docker编排配置
└── docs/                   # 文档
```

## 📚 API 文档

### 用户认证

#### 用户注册
```
POST /api/v1/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### 用户登录
```
POST /api/v1/auth/login/access-token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

### 模板管理 (管理员)

#### 创建模板
```
POST /api/v1/admin/templates/
Authorization: Bearer <JWT_TOKEN>

{
  "title": "复古风格模板",
  "category": "复古",
  "cover_image_url": "http://localhost:8000/static/uploads/...",
  "price": 9.9,
  "prompt_config": {
    "base_prompt": "vintage style",
    "variable_prompt": "coat",
    "negative_prompt": "..."
  }
}
```

#### 删除模板
```
DELETE /api/v1/admin/templates/{id}
Authorization: Bearer <JWT_TOKEN>
```

### 订单管理

#### 创建订单
```
POST /api/v1/orders/
Authorization: Bearer <JWT_TOKEN>

{
  "template_id": "template-uuid"
}
```

#### 查询订单
```
GET /api/v1/orders/{order_id}
Authorization: Bearer <JWT_TOKEN>
```

## 🔧 管理员功能

### 默认管理员账户

系统初始化时会自动创建默认管理员账户：
- 邮箱: `admin@superstar.ai`
- 密码: `admin123`

### 管理员权限

- 模板管理: 创建、删除模板
- 用户管理: 查看用户列表
- 数据看板: 实时运营数据监控

## 📊 数据看板

管理员可通过 `/api/v1/admin/stats/dashboard` 接口获取实时运营数据，包括：
- 总用户数
- 总收入
- 完成订单数
- 模板数量

## 🚢 部署

### 生产环境部署

使用Docker Compose进行生产环境部署：

```bash
# 构建并启动生产环境
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 环境变量配置

生产环境需要配置以下环境变量：

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/superstar_db

# Redis配置
REDIS_URL=redis://redis:6379

# JWT配置
SECRET_KEY=your_very_long_and_secure_secret_key

# 外部服务配置
VOLCANO_API_KEY=your_volcano_api_key
VOLCANO_SECRET_KEY=your_volcano_secret_key
```

## 🛠️ 开发指南

### 本地开发

1. 后端开发
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. 前端开发
```bash
cd frontend
# 使用任何静态文件服务器，如:
npx serve .
```

### 代码结构说明

- `backend/app/api/v1/` - API路由定义
- `backend/app/models/` - 数据库模型
- `backend/app/schemas/` - 数据验证模型
- `backend/app/core/` - 核心配置和依赖
- `frontend/index.html` - 前端单页面应用

## 📈 未来发展方向

- 集成AI图像生成服务 (如火山引擎)
- 增加更多模板和风格选项
- 实现社交功能和社区画廊
- 移动端适配
- 国际化支持

## 🤝 贡献

欢迎提交PR和Issue。请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 支持

如需支持，请联系: admin@superstar.ai