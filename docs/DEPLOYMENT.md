# Superstar AI 部署文档

## 1. 环境要求

### 1.1 硬件要求

- **CPU**: 4核或更高
- **内存**: 8GB RAM 或更高（推荐16GB）
- **存储**: 100GB 可用空间
- **网络**: 稳定的互联网连接

### 1.2 软件要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+), macOS, 或 Windows 10+
- **Docker**: 20.10.0 或更高版本
- **Docker Compose**: 2.0.0 或更高版本
- **Git**: 2.25.0 或更高版本

### 1.3 依赖服务

- **PostgreSQL**: 14 或更高版本（生产环境）
- **Redis**: 7 或更高版本
- **Python**: 3.8 或更高版本（如使用手动部署）

## 2. 部署方式

### 2.1 Docker Compose 部署（推荐）

这是最简单和推荐的部署方式，适合生产环境和开发环境。

#### 2.1.1 环境准备

1. 安装 Docker 和 Docker Compose
2. 克隆项目代码
3. 配置环境变量

#### 2.1.2 部署步骤

1. **克隆代码仓库**
   ```bash
   git clone https://github.com/lawye5718/superstar2.git
   cd superstar2
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入实际的配置值
   vim .env
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **检查服务状态**
   ```bash
   docker-compose ps
   ```

#### 2.1.3 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# 应用配置
APP_NAME=Superstar AI
APP_VERSION=2.0.0

# 数据库配置
POSTGRES_DB=superstar_db
POSTGRES_USER=user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://user:your_secure_password@db:5432/superstar_db

# Redis 配置
REDIS_URL=redis://redis:6379

# JWT 配置
SECRET_KEY=your_very_long_and_secure_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 外部服务配置
VOLCANO_API_KEY=your_volcano_api_key
VOLCANO_SECRET_KEY=your_volcano_secret_key

# CDN 和存储
CDN_DOMAIN=your-cdn-domain.com
STORAGE_TYPE=cos  # cos, s3, or local
```

### 2.2 手动部署

适用于需要更多控制的生产环境。

#### 2.2.1 环境准备

1. **安装 Python 依赖**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   pip install -r backend/requirements.txt
   ```

2. **安装并配置 PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib
   sudo postgresql-setup --initdb
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

3. **创建数据库**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE superstar_db;
   CREATE USER user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE superstar_db TO user;
   \q
   ```

4. **安装并配置 Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   
   # CentOS/RHEL
   sudo yum install redis
   sudo systemctl start redis
   sudo systemctl enable redis
   ```

#### 2.2.2 启动应用

1. **设置环境变量**
   ```bash
   export DATABASE_URL=postgresql+asyncpg://user:your_secure_password@localhost/superstar_db
   export REDIS_URL=redis://localhost:6379
   export SECRET_KEY=your_very_long_and_secure_secret_key
   ```

2. **启动后端服务**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **启动 Celery Worker**
   ```bash
   cd backend
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

4. **部署前端**
   将 `frontend/index.html` 及相关资源部署到 Web 服务器（如 Nginx）。

## 3. Docker Compose 详解

### 3.1 服务组成

Superstar AI 由以下服务组成：

- **backend**: FastAPI 应用服务
- **redis**: Redis 缓存和消息队列
- **worker**: Celery 工作进程
- **frontend**: 前端 Nginx 服务（可选）

### 3.2 docker-compose.yml 说明

```yaml
version: '3.8'

services:
  # 1. 后端 API 服务
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
      - SECRET_KEY=supersecretkey123
    command: sh -c "python scripts/init_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    depends_on:
      - redis

  # 2. Redis (消息队列)
  redis:
    image: redis:alpine
    container_name: superstar_redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  # 3. Celery Worker (AI 任务执行者)
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
      - ./data/db:/app/db_data
    depends_on:
      - backend
      - redis

  # 4. 前端 (Nginx 托管静态文件)
  frontend:
    build:
      context: ./frontend
    container_name: superstar_frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
```

## 4. 配置管理

### 4.1 环境变量详解

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| APP_NAME | Superstar AI | 应用名称 |
| APP_VERSION | 2.0.0 | 应用版本 |
| DATABASE_URL | sqlite+aiosqlite:///./superstar.db | 数据库连接字符串 |
| DATABASE_SYNC_URL | sqlite:///./superstar.db | 同步数据库连接字符串 |
| SECRET_KEY | 随机字符串 | JWT密钥，生产环境必须修改 |
| ALGORITHM | HS256 | JWT算法 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | 访问令牌过期时间（分钟） |
| REDIS_URL | redis://localhost:6379 | Redis连接地址 |
| VOLCANO_API_KEY | | 火山引擎API密钥 |
| VOLCANO_SECRET_KEY | | 火山引擎密钥 |
| CDN_DOMAIN | | CDN域名 |
| STORAGE_TYPE | local | 存储类型 (local, cos, s3) |

### 4.2 安全配置

1. **修改默认密钥**
   - 生产环境必须修改 `SECRET_KEY`
   - 建议使用 `openssl rand -hex 32` 生成

2. **数据库安全**
   - 使用强密码
   - 定期备份
   - 限制数据库访问权限

3. **API密钥管理**
   - 不要将API密钥硬编码在代码中
   - 定期轮换密钥

## 5. 监控和日志

### 5.1 应用日志

应用日志输出到控制台，可以通过 Docker 查看：

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f worker
```

### 5.2 系统监控

#### 5.2.1 健康检查端点

- **应用健康**: `GET /health`
- **数据库连接**: 通过应用内部检查
- **外部服务**: 通过应用内部检查

#### 5.2.2 监控脚本示例

创建监控脚本 `monitor.sh`:

```bash
#!/bin/bash

# 检查应用健康状态
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ $HEALTH_STATUS -ne 200 ]; then
    echo "$(date): Application is unhealthy (Status: $HEALTH_STATUS)" | mail -s "Superstar AI Alert" admin@yourdomain.com
fi

# 检查 Docker 服务状态
docker-compose ps --format "table {{.Name}}\t{{.Status}}" | grep -E "(unhealthy|Exited|Paused)"
```

## 6. 备份和恢复

### 6.1 数据备份

```bash
# 备份数据库
docker exec -t superstar_db pg_dump -U user superstar_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份静态文件
tar -czf static_backup_$(date +%Y%m%d_%H%M%S).tar.gz ./data/static/
```

### 6.2 数据恢复

```bash
# 恢复数据库
docker exec -i superstar_db psql -U user -d superstar_db < backup_file.sql
```

## 7. 性能优化

### 7.1 数据库优化

1. **索引优化**
   - 为常用查询字段创建索引
   - 定期分析查询性能

2. **连接池配置**
   - 根据应用负载调整连接池大小
   - 配置连接超时时间

### 7.2 缓存策略

1. **Redis缓存**
   - 缓存热门模板
   - 缓存用户会话

2. **CDN加速**
   - 静态资源使用CDN分发
   - 图片压缩和优化

## 8. 故障排除

### 8.1 常见问题

#### 问题1: 服务无法启动
**症状**: `docker-compose up` 后服务立即退出
**解决方案**: 
- 检查 `.env` 文件配置
- 查看详细日志 `docker-compose logs backend`

#### 问题2: 数据库连接失败
**症状**: 应用启动时报告数据库连接错误
**解决方案**:
- 确认数据库服务已启动
- 检查数据库连接字符串

#### 问题3: 文件上传失败
**症状**: 上传文件时返回错误
**解决方案**:
- 检查存储目录权限
- 确认磁盘空间充足

### 8.2 诊断命令

```bash
# 检查容器状态
docker-compose ps

# 检查容器资源使用
docker stats

# 进入容器调试
docker-compose exec backend bash

# 重启特定服务
docker-compose restart backend
```

## 9. 升级指南

### 9.1 版本升级

1. **备份数据**
   ```bash
   # 备份数据库和静态文件
   ```

2. **拉取最新代码**
   ```bash
   git pull origin main
   ```

3. **更新依赖**
   ```bash
   docker-compose build --no-cache
   ```

4. **启动服务**
   ```bash
   docker-compose up -d
   ```

## 10. 安全配置

### 10.1 SSL 配置

使用 Let's Encrypt 获取免费 SSL 证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 10.2 防火墙配置

```bash
# 只开放必要的端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 11. 扩展配置

### 11.1 负载均衡

对于高流量场景，可配置 Nginx 作为反向代理：

```nginx
upstream superstar_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://superstar_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 11.2 集群部署

对于大规模部署，可考虑以下架构：
- 多个后端实例
- 负载均衡器
- 数据库主从复制
- Redis集群