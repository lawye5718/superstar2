# Superstar AI - 快速启动指南

## 环境要求

- Python 3.8+ (推荐 3.11 或 3.12)
- pip (Python 包管理器)

## 前端启动方法

前端是一个基于 Vue 3 CDN 的单文件应用（`frontend/index.html`），**无需构建步骤**。

### 方式一：直接用浏览器打开

```bash
# 直接在浏览器中打开 frontend/index.html 文件
open frontend/index.html          # macOS
xdg-open frontend/index.html      # Linux
start frontend\index.html         # Windows
```

> **注意**：直接从文件系统打开时浏览器会施加 CORS 限制，API 请求可能被阻止。
> 建议使用方式二或以上方式以获得完整功能。

### 方式二：使用 Python 内置 HTTP 服务器（推荐开发环境）

```bash
cd frontend
python -m http.server 3000
```

然后访问 http://localhost:3000

### 方式三：使用 Docker

```bash
docker build -t superstar-frontend ./frontend
docker run -p 3000:80 superstar-frontend
```

然后访问 http://localhost:3000

### 方式四：使用 Docker Compose（全栈）

```bash
docker-compose up
```

- 前端：http://localhost:3000
- 后端：http://localhost:8000

## 后端安装步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

复制 `.env.example` 到 `.env` 并根据需要修改:

```bash
cp .env.example .env
```

默认配置使用SQLite数据库，无需额外配置即可运行。

### 3. 启动服务器

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

或者使用热重载模式（开发环境）:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务器启动后会自动：
- 创建数据库表
- 初始化示例数据（1个用户和6个模板）

## 访问应用

### API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 健康检查
```bash
curl http://localhost:8000/health
```

## 测试API

### 1. 获取模板列表
```bash
curl http://localhost:8000/api/v1/templates/
```

### 2. 生成测试Token
```bash
cd backend
python << 'EOF'
from app.core.dependencies import create_access_token
from datetime import timedelta

token = create_access_token(
    data={"sub": "test-user-uuid-001"},
    expires_delta=timedelta(hours=24)
)
print(f"Token: {token}")
EOF
```

### 3. 获取用户信息
```bash
TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me
```

### 4. 创建订单
```bash
TOKEN="your_token_here"
TEMPLATE_ID=$(curl -s http://localhost:8000/api/v1/templates/ | python -c "import sys, json; print(json.load(sys.stdin)[0]['id'])")

curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"template_id\": \"$TEMPLATE_ID\"}" \
  http://localhost:8000/api/v1/orders/
```

## 默认账户

应用启动时会创建一个演示账户：
- 用户ID: `test-user-uuid-001`
- 邮箱: `demo@example.com`
- 积分: 100

## 项目结构

```
backend/
├── app/
│   ├── api/v1/          # API路由
│   │   ├── admin/       # 管理员API
│   │   ├── users.py     # 用户API
│   │   ├── templates.py # 模板API
│   │   ├── orders.py    # 订单API
│   │   └── utils.py     # 工具API
│   ├── core/            # 核心配置
│   │   ├── config.py    # 应用配置
│   │   ├── database.py  # 数据库配置
│   │   ├── dependencies.py # 依赖注入
│   │   └── security.py  # 安全工具
│   ├── models/          # 数据模型
│   │   └── database.py  # SQLAlchemy模型
│   ├── schemas/         # Pydantic模型
│   ├── services/        # 业务逻辑
│   ├── middleware/      # 中间件
│   └── main.py          # 应用入口
├── scripts/             # 脚本
│   └── init_data.py     # 数据初始化
├── requirements.txt     # 依赖
└── static/              # 静态文件
    └── uploads/         # 上传文件存储
```

## 数据库

### SQLite (默认)
- 数据库文件: `backend/superstar.db`
- 自动创建，无需手动配置

### PostgreSQL (生产环境)
修改 `.env` 文件:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/superstar_db
DATABASE_SYNC_URL=postgresql://user:password@localhost/superstar_db
```

## 常见问题

### 1. 端口已被占用
修改启动命令中的端口号:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. 依赖安装失败
尝试使用虚拟环境:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. 数据库错误
删除数据库文件重新启动:
```bash
rm backend/superstar.db
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 开发建议

1. 使用虚拟环境隔离依赖
2. 在开发环境使用SQLite，生产环境使用PostgreSQL
3. 定期备份数据库
4. 修改默认SECRET_KEY（在 `.env` 文件中）
5. 启用CORS时限制允许的域名

## 更多信息

- 详细文档: `docs/`
- API文档: `docs/API.md`
- 架构文档: `docs/ARCHITECTURE.md`
- 测试报告: `TEST_REPORT.md`
