# Superstar AI - 项目目录结构说明

## 1. 项目根目录结构

```
superstar2/
├── backend/                    # 后端代码目录
│   ├── app/                   # 核心应用代码
│   │   ├── __init__.py        # 应用初始化
│   │   ├── api/              # API路由定义
│   │   │   ├── __init__.py
│   │   │   └── v1/           # API版本1
│   │   │       ├── __init__.py
│   │   │       ├── admin/     # 管理员相关API
│   │   │       │   ├── __init__.py
│   │   │       │   ├── stats.py      # 管理员统计API
│   │   │       │   └── templates.py  # 管理员模板API
│   │   │       ├── auth.py    # 认证相关API
│   │   │       ├── galleries.py # 画廊相关API
│   │   │       ├── orders.py  # 订单相关API
│   │   │       ├── router.py  # 路由注册中心
│   │   │       ├── tasks.py   # 任务相关API
│   │   │       ├── templates.py # 模板相关API
│   │   │       ├── users.py   # 用户相关API
│   │   │       └── utils.py   # 工具相关API
│   │   ├── core/             # 核心组件
│   │   │   ├── __init__.py
│   │   │   ├── config.py     # 应用配置
│   │   │   ├── database.py   # 数据库连接配置
│   │   │   ├── dependencies.py # 依赖注入
│   │   │   ├── exceptions.py # 自定义异常
│   │   │   ├── security.py   # 安全相关
│   │   │   └── validators.py # 数据验证
│   │   ├── database/         # 数据库相关
│   │   ├── middleware/       # 中间件
│   │   │   ├── __init__.py
│   │   │   └── logging.py    # 日志中间件
│   │   ├── models/           # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── database.py   # 数据库模型定义
│   │   │   └── enums.py      # 枚举定义
│   │   ├── schemas/          # Pydantic模型
│   │   │   ├── __init__.py
│   │   │   ├── admin.py      # 管理员相关Schema
│   │   │   ├── auth.py       # 认证相关Schema
│   │   │   ├── base.py       # 基础Schema
│   │   │   ├── orders.py     # 订单相关Schema
│   │   │   ├── template.py   # 模板相关Schema
│   │   │   └── user.py       # 用户相关Schema
│   │   ├── services/         # 业务逻辑服务
│   │   │   ├── __init__.py
│   │   │   ├── admin.py      # 管理员服务
│   │   │   ├── auth.py       # 认证服务
│   │   │   ├── order.py      # 订单服务
│   │   │   ├── template.py   # 模板服务
│   │   │   └── user.py       # 用户服务
│   │   └── utils/            # 工具函数
│   ├── scripts/              # 脚本目录
│   │   ├── __init__.py
│   │   └── init_data.py      # 初始化数据脚本
│   ├── static/               # 静态文件目录
│   │   └── uploads/          # 上传文件存储
│   ├── tests/                # 测试目录
│   ├── venv/                 # 虚拟环境目录
│   ├── .env.example          # 环境变量示例
│   ├── .gitignore            # Git忽略配置
│   ├── Dockerfile            # 后端Docker配置
│   ├── README.md             # 后端说明文档
│   └── requirements.txt      # Python依赖
├── frontend/                 # 前端代码目录
│   ├── index.html            # 主页面文件
│   ├── assets/               # 静态资源
│   ├── public/               # 公共资源
│   └── src/                  # 源代码目录
├── docs/                     # 文档目录
│   ├── API.md                # API文档
│   ├── DEPLOYMENT.md         # 部署文档
│   ├── DEVELOPMENT.md        # 开发指南
│   └── ARCHITECTURE.md       # 架构文档
├── .env                      # 环境变量配置
├── .gitignore                # Git忽略配置
├── CODE_REVIEW_COMPLETE.md   # 代码审查文档
├── QUICK_START.md            # 快速开始文档
├── README.md                 # 项目说明文档
├── TEST_REPORT.md            # 测试报告
├── docker-compose.yml        # Docker编排配置
├── merge_branches.py         # 分支合并脚本
└── TECHNICAL_DOCUMENTATION.md # 技术文档
```

## 2. 后端目录详细说明

### 2.1 backend/app/api/v1/ - API路由层

这是应用的API路由层，负责处理所有HTTP请求：

- **admin/** - 管理员专用API
  - `stats.py`: 管理员数据统计相关API
  - `templates.py`: 管理员模板管理相关API

- **核心API模块**:
  - `auth.py`: 用户认证相关接口（登录、注册、令牌刷新）
  - `galleries.py`: 画廊相关接口
  - `orders.py`: 订单管理相关接口
  - `tasks.py`: 任务管理相关接口
  - `templates.py`: 模板管理相关接口
  - `users.py`: 用户管理相关接口
  - `utils.py`: 工具相关接口（文件上传等）
  - `router.py`: 所有路由的集中注册点

### 2.2 backend/app/core/ - 核心组件

- `config.py`: 应用配置管理，包含所有环境变量定义
- `database.py`: 数据库连接配置，包含同步和异步连接
- `dependencies.py`: 依赖注入，包含认证、数据库连接等依赖
- `exceptions.py`: 自定义异常类定义
- `security.py`: 安全相关功能（密码加密、JWT令牌等）
- `validators.py`: 数据验证相关功能

### 2.3 backend/app/models/ - 数据模型层

- `database.py`: SQLAlchemy数据模型定义
- `enums.py`: 枚举类型定义

### 2.4 backend/app/schemas/ - 数据传输对象层

- `admin.py`: 管理员相关数据传输对象
- `auth.py`: 认证相关数据传输对象
- `base.py`: 基础数据传输对象
- `orders.py`: 订单相关数据传输对象
- `template.py`: 模板相关数据传输对象
- `user.py`: 用户相关数据传输对象

### 2.5 backend/app/services/ - 业务逻辑层

- `admin.py`: 管理员业务逻辑
- `auth.py`: 认证业务逻辑
- `order.py`: 订单业务逻辑
- `template.py`: 模板业务逻辑
- `user.py`: 用户业务逻辑

### 2.6 backend/scripts/ - 初始化脚本

- `init_data.py`: 应用启动时的初始化脚本，用于创建管理员账户和示例数据

### 2.7 backend/static/ - 静态文件

- `uploads/`: 用户上传的文件存储目录

## 3. 前端目录结构

### 3.1 frontend/index.html

前端单页面应用的主文件，包含：

- Vue 3 Composition API 实现
- Tailwind CSS 样式
- Axios HTTP客户端
- 完整的前端业务逻辑

### 3.2 前端功能模块

- **导航模块**: 页面导航和路由管理
- **认证模块**: 用户登录/注册功能
- **相机模块**: 模板展示和选择功能
- **画廊模块**: 模板浏览和购买功能
- **管理员模块**: 模板管理、用户管理、数据看板
- **订单模块**: 订单管理和结果展示
- **用户模块**: 个人信息和余额管理

## 4. 配置文件说明

### 4.1 环境配置

- `.env.example`: 环境变量配置示例文件
- `.env`: 实际环境变量配置文件（已加入.gitignore）

### 4.2 依赖管理

- `backend/requirements.txt`: Python依赖列表
- `frontend/package.json`: 前端依赖（如果使用）

### 4.3 Docker配置

- `docker-compose.yml`: 多服务编排配置
- `backend/Dockerfile`: 后端容器构建配置

## 5. 文档目录

### 5.1 技术文档

- `docs/API.md`: 详细的API接口文档
- `docs/DEPLOYMENT.md`: 部署指南和配置说明
- `docs/DEVELOPMENT.md`: 开发环境搭建和开发指南
- `docs/ARCHITECTURE.md`: 系统架构说明

### 5.2 项目文档

- `README.md`: 项目总体说明
- `QUICK_START.md`: 快速开始指南
- `TEST_REPORT.md`: 测试报告
- `CODE_REVIEW_COMPLETE.md`: 代码审查报告

## 6. 代码组织原则

### 6.1 分层架构

项目遵循典型的分层架构模式：

```
表现层 (API) -> 业务逻辑层 -> 数据访问层 -> 数据模型层
```

- **API层**: 处理HTTP请求和响应
- **服务层**: 实现业务逻辑
- **数据访问层**: 处理数据库操作
- **模型层**: 定义数据结构

### 6.2 模块化设计

每个功能模块都有独立的目录结构，便于维护和扩展：

- 按功能划分模块
- 每个模块包含API、服务、模型和Schema
- 模块间保持松耦合

### 6.3 配置分离

- 配置与代码分离
- 环境相关配置通过环境变量管理
- 敏感信息不在代码中硬编码

## 7. 部署相关

### 7.1 Docker相关

- `docker-compose.yml`: 多容器编排
- `backend/Dockerfile`: 后端镜像构建
- `frontend/Dockerfile`: 前端镜像构建（如果有）

### 7.2 初始化脚本

- `backend/scripts/init_data.py`: 应用启动初始化
- 数据库表创建
- 管理员账户创建
- 示例数据填充

## 8. 测试相关

### 8.1 测试目录结构

```
backend/tests/
├── __init__.py
├── conftest.py          # 测试配置
├── test_auth.py         # 认证测试
├── test_users.py        # 用户测试
├── test_templates.py    # 模板测试
├── test_orders.py       # 订单测试
└── fixtures/            # 测试固件
```

### 8.2 测试策略

- 单元测试：测试独立函数和方法
- 集成测试：测试API端点和数据库交互
- 端到端测试：测试完整用户流程

---

此目录结构文档为Superstar AI项目的完整结构说明，有助于新开发人员快速了解项目组织方式和代码布局。