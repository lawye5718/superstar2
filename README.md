# Superstar AI - 已修改版本

此项目基于原始的Superstar AI代码库进行了多项改进，以解决前后端连接问题并实现可运行、可测试的版本。

## 主要修改内容

### 1. 前后端连接
- 移除了前端的模拟数据和mockAxios拦截器
- 将API_BASE指向真实的后端地址 `http://localhost:8000/api/v1`
- 实现了真实的API调用，包括用户认证、模板获取、订单创建等功能

### 2. 用户认证系统
- 实现了基于JWT的真实身份验证系统
- 创建了`dependencies.py`处理认证逻辑
- 添加了`get_current_user_id`函数从JWT token中解析用户ID

### 3. 数据库模型增强
- 在`Template`模型中添加了`price`和`usage_count`字段
- 在`Order`模型中添加了`template_id`和`result_image_url`字段
- 添加了积分消耗字段`credits_consumed`

### 4. API端点实现
- **用户API**: 实现了`/users/me`和`/users/face`端点，支持获取用户信息和上传头像
- **模板API**: 实现了`/templates/random`和`/templates/`端点，支持随机获取模板和分类筛选
- **订单API**: 实现了`/orders/`和`/orders/{order_id}`端点，支持创建订单和查询订单状态

### 5. 数据库连接优化
- 根据数据库URL动态配置连接参数，仅在使用SQLite时添加`check_same_thread`参数
- 修复了PostgreSQL连接参数配置问题

### 6. 静态文件支持
- 添加了对上传文件的静态服务支持
- 配置了`/static`路径以提供上传的图片文件

### 7. 初始化脚本
- 创建了`scripts/init_data.py`用于初始化示例数据
- 自动创建示例用户和模板数据

## 运行说明

### 环境要求
- Python 3.8+ (建议使用3.11或3.12以避免兼容性问题)
- PostgreSQL (生产环境) 或 SQLite (开发环境)

### 安装依赖
```bash
pip install -r backend/requirements.txt
```

### 启动应用
```bash
cd backend
uvicorn app.main:app --reload
```

### 数据库初始化
应用启动时会自动初始化数据库和示例数据。

## 功能特性

1. **用户系统**: 用户认证、头像上传、余额管理
2. **模板系统**: 模板展示、随机模板、分类筛选
3. **订单系统**: 订单创建、状态查询、结果展示
4. **文件上传**: 用户头像上传功能
5. **真实API**: 所有功能都连接到真实的后端服务

## 技术架构

- **前端**: Vue 3 + Tailwind CSS + Axios
- **后端**: FastAPI + SQLAlchemy + PostgreSQL/SQLite
- **认证**: JWT Token
- **文件存储**: 本地文件系统（生产环境建议使用云存储）

## 项目结构

```
superstar_workspace/
├── backend/              # 后端代码
│   ├── app/              # 应用代码
│   │   ├── api/v1/       # API路由
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic模型
│   │   ├── services/     # 业务逻辑
│   │   └── core/         # 核心配置
│   ├── scripts/          # 初始化脚本
│   └── requirements.txt  # 依赖文件
├── frontend/             # 前端代码
│   └── index.html        # 主页面
└── README.md             # 项目说明
```

## 已解决问题

1. ✅ 前后端连接问题 - 前端现在连接到真实后端
2. ✅ 硬编码身份验证 - 实现了JWT认证系统
3. ✅ 数据库连接参数 - 修复了SQLite/PostgreSQL连接问题
4. ✅ 文件上传功能 - 实现了真实的文件上传接口
5. ✅ 模板价格和统计 - 添加了价格和使用次数字段
6. ✅ 订单系统 - 实现了完整的订单流程

## 待完善功能

1. 实现完整的支付系统
2. 集成AI生成服务
3. 添加异步任务处理（Celery）
4. 实现用户注册和登录功能
5. 添加更多安全措施

## 开发辅助工具

- `merge_branches.py`: 依提交时间顺序将所有本地分支合并到指定分支，支持 `--dry-run` 查看计划。
