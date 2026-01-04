# Superstar AI 部署文档

## 1. 环境要求

### 1.1 硬件要求

- **CPU**: 2核或更高
- **内存**: 4GB RAM 或更高（推荐8GB）
- **存储**: 50GB 可用空间
- **网络**: 稳定的互联网连接

### 1.2 软件要求

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 8+), macOS, 或 Windows 10+
- **Docker**: 20.10.0 或更高版本
- **Docker Compose**: 2.0.0 或更高版本
- **Git**: 2.25.0 或更高版本

### 1.3 依赖服务

- **PostgreSQL**: 14 或更高版本
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
   pip install -r requirements.txt
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

#### 2.2.2 启动服务

1. **后端服务**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **前端服务**
   ```bash
   # 使用 Nginx 或其他 Web 服务器部署前端文件
   sudo cp -r frontend/* /var/www/html/
   ```

## 3. 数据库管理

### 3.1 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 进入后端目录
cd backend

# 检查当前版本
alembic current

# 升级到最新版本
alembic upgrade head

# 创建新迁移
alembic revision --autogenerate -m "描述迁移内容"

# 回滚到上一个版本
alembic downgrade -1
```

### 3.2 数据备份

```bash
# 备份数据库
pg_dump -h localhost -U user -d superstar_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
psql -h localhost -U user -d superstar_db < backup_file.sql
```

## 4. 服务管理

### 4.1 Docker Compose 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看服务日志
docker-compose logs -f backend

# 查看服务状态
docker-compose ps
```

### 4.2 后端服务配置

#### 4.2.1 Gunicorn 配置（生产环境）

创建 `gunicorn.conf.py`:

```python
# Gunicorn 配置
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

启动命令：
```bash
gunicorn app.main:app -c gunicorn.conf.py
```

#### 4.2.2 Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/static/files/;
        expires 30d;
    }
}
```

## 5. 监控和日志

### 5.1 应用日志

应用日志输出到控制台，可以通过 Docker 查看：

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看所有服务日志
docker-compose logs -f
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

## 6. 安全配置

### 6.1 SSL 配置

使用 Let's Encrypt 获取免费 SSL 证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 6.2 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 6.3 安全最佳实践

1. **定期更新依赖包**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **使用强密码**
   - 数据库密码
   - JWT 密钥
   - API 密钥

3. **限制访问权限**
   - 数据库访问权限
   - 文件系统权限
   - API 访问限制

## 7. 性能优化

### 7.1 数据库优化

1. **索引优化**
   - 为经常查询的字段创建索引
   - 定期分析查询计划

2. **连接池配置**
   - 调整数据库连接池大小
   - 配置连接超时时间

### 7.2 缓存策略

1. **Redis 缓存**
   - 缓存热门数据
   - 实现会话存储

2. **CDN 配置**
   - 静态资源加速
   - 图片压缩和优化

### 7.3 负载均衡

使用 Nginx 或 HAProxy 实现负载均衡：

```nginx
upstream backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
    }
}
```

## 8. 故障排除

### 8.1 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 检查连接字符串配置
   - 检查防火墙设置

2. **Redis 连接失败**
   - 检查 Redis 服务状态
   - 检查连接 URL 配置

3. **应用启动失败**
   - 检查依赖包安装
   - 检查环境变量配置
   - 查看应用日志

### 8.2 诊断命令

```bash
# 检查服务状态
docker-compose ps

# 检查日志
docker-compose logs backend

# 检查网络连接
docker-compose exec backend ping db
docker-compose exec backend ping redis

# 检查数据库连接
docker-compose exec backend python -c "import sqlalchemy; engine = sqlalchemy.create_engine('your_db_url'); engine.connect()"
```

## 9. 备份和恢复

### 9.1 自动备份脚本

创建备份脚本 `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backup/superstar"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec db pg_dump -U user -d superstar_db > $BACKUP_DIR/db_backup_$DATE.sql

# 备份配置文件
cp .env $BACKUP_DIR/config_$DATE.env

# 压缩备份文件
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR db_backup_$DATE.sql config_$DATE.env

# 删除7天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.tar.gz"
```

### 9.2 恢复步骤

1. **停止服务**
   ```bash
   docker-compose down
   ```

2. **恢复数据库**
   ```bash
   docker-compose exec -T db psql -U user -d superstar_db < backup_file.sql
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

## 10. 升级指南

### 10.1 小版本升级

1. **拉取最新代码**
   ```bash
   git pull origin main
   ```

2. **更新依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **执行数据库迁移**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **重启服务**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### 10.2 大版本升级

1. **备份数据**
2. **阅读升级说明**
3. **在测试环境验证**
4. **执行升级**
5. **验证功能**

---
**文档版本**: 1.0  
**最后更新**: 2025-01-04