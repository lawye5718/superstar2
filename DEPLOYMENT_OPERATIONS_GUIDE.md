# Superstar AI - 部署和运维指南

## 1. 部署前准备

### 1.1 环境要求

**硬件要求**:
- CPU: 4核或更高
- 内存: 8GB RAM 或更高（推荐16GB）
- 存储: 100GB 可用空间
- 网络: 稳定的互联网连接

**软件要求**:
- Docker: 20.10.0 或更高版本
- Docker Compose: 2.0.0 或更高版本
- Git: 2.25.0 或更高版本

**可选服务**:
- PostgreSQL: 14 或更高版本（生产环境）
- Redis: 7 或更高版本

### 1.2 系统检查清单

在开始部署前，请确认以下条件已满足：

- [ ] 服务器硬件满足最低要求
- [ ] Docker 和 Docker Compose 已安装并正常运行
- [ ] 有足够的磁盘空间
- [ ] 网络连接正常
- [ ] 防火墙已配置允许必要端口
- [ ] 域名已解析到服务器IP

## 2. 部署流程

### 2.1 代码获取

```bash
# 克隆代码仓库
git clone https://github.com/lawye5718/superstar2.git
cd superstar2
```

### 2.2 环境配置

#### 2.2.1 环境变量配置

创建 `.env` 文件并配置：

```bash
# 复制环境变量模板
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```bash
# 应用配置
APP_NAME=Superstar AI
APP_VERSION=2.0.0

# 数据库配置
POSTGRES_DB=superstar_db
POSTGRES_USER=superstar_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://superstar_user:your_secure_password@db:5432/superstar_db

# Redis 配置
REDIS_URL=redis://redis:6379

# JWT 配置 (务必修改!)
SECRET_KEY=your_very_long_and_secure_random_string_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 外部服务配置
VOLCANO_API_KEY=your_volcano_api_key
VOLCANO_SECRET_KEY=your_volcano_secret_key

# CDN 和存储
CDN_DOMAIN=your-cdn-domain.com
STORAGE_TYPE=local  # local, cos, s3
```

**重要安全提醒**:
- `SECRET_KEY` 必须使用足够长的随机字符串
- `POSTGRES_PASSWORD` 必须使用强密码
- 外部API密钥应使用生产环境的密钥

#### 2.2.2 安全配置检查

```bash
# 生成安全的SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.3 Docker Compose 配置

检查 `docker-compose.yml` 文件确保配置正确：

```yaml
version: '3.8'

services:
  # 后端 API 服务
  backend:
    build: 
      context: ./backend
    container_name: superstar_backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app                # 代码热更新（开发环境）
      - ./data/static:/app/static     # 图片持久化
      - ./data/db:/app/db_data        # 数据库持久化
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    command: sh -c "python scripts/init_data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    depends_on:
      - redis

  # Redis (消息队列)
  redis:
    image: redis:alpine
    container_name: superstar_redis
    ports:
      - "6379:6379"
    restart: unless-stopped

  # Celery Worker (AI 任务执行者)
  worker:
    build: 
      context: ./backend
    container_name: superstar_worker
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./backend:/app
      - ./data/static:/app/static
      - ./data/db:/app/db_data
    depends_on:
      - backend
      - redis

  # 前端 (Nginx 托管静态文件)
  frontend:
    build:
      context: ./frontend
    container_name: superstar_frontend
    ports:
      - "80:80"  # 生产环境通常映射到80端口
    depends_on:
      - backend
```

### 2.4 数据持久化配置

确保数据持久化目录已创建：

```bash
# 创建数据持久化目录
mkdir -p data/static
mkdir -p data/db

# 设置适当的权限
chmod -R 755 data/
```

### 2.5 部署执行

#### 2.5.1 构建和启动服务

```bash
# 构建并启动所有服务
docker-compose up --build -d

# 或者分别启动服务
docker-compose build
docker-compose up -d
```

#### 2.5.2 服务状态检查

```bash
# 检查服务状态
docker-compose ps

# 检查特定服务日志
docker-compose logs backend
docker-compose logs worker
docker-compose logs redis
```

预期输出应显示所有服务都在运行：

```
      Name                     Command               State           Ports
-----------------------------------------------------------------------------------
superstar_backend    uvicorn app.main:app --ho ...   Up      0.0.0.0:8000->8000/tcp
superstar_frontend   nginx -g daemon off;             Up      0.0.0.0:80->80/tcp
superstar_redis      docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
superstar_worker     celery -A app.tasks.celer ...    Up
```

### 2.6 健康检查

```bash
# 检查应用健康状态
curl http://localhost/health

# 检查API文档
curl http://localhost/docs

# 检查前端是否正常加载
curl http://localhost
```

## 3. 运维操作

### 3.1 日常运维任务

#### 3.1.1 查看日志

```bash
# 实时查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f worker

# 查看最近的错误日志
docker-compose logs --tail=100 --since=1h | grep -i error
```

#### 3.1.2 资源监控

```bash
# 查看容器资源使用情况
docker stats

# 查看特定容器
docker stats superstar_backend superstar_worker
```

#### 3.1.3 性能监控

```bash
# 检查API响应时间
time curl -s http://localhost/api/v1/health

# 检查数据库连接
docker-compose exec backend python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
print('Database connection OK')
"
```

### 3.2 服务管理

#### 3.2.1 服务启停

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 重新部署（重建镜像）
docker-compose up --build -d
```

#### 3.2.2 配置更新

```bash
# 更新配置后重新加载
docker-compose down
docker-compose up -d

# 或者只重启需要重新加载的服务
docker-compose restart backend worker
```

### 3.3 备份和恢复

#### 3.3.1 数据库备份

```bash
# 备份数据库
docker-compose exec db pg_dump -U superstar_user superstar_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 或者使用卷备份
docker run --rm -v superstar2_data-db:/source -v $(pwd)/backup:/backup alpine tar czf /backup/db_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
```

#### 3.3.2 静态文件备份

```bash
# 备份上传的文件
tar -czf static_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C data/static/ .
```

#### 3.3.3 完整备份脚本

创建备份脚本 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting backup..."

# 停止服务
docker-compose down

# 备份数据库
docker run --rm -v superstar2_postgres_data:/pgdata -o alpine tar czf - -C /pgdata . > "$BACKUP_DIR/db.tar.gz"

# 备份静态文件
tar czf "$BACKUP_DIR/static.tar.gz" -C data/static/ .

# 备份配置文件
cp .env "$BACKUP_DIR/env.backup"
cp docker-compose.yml "$BACKUP_DIR/docker-compose.yml.backup"

echo "Backup completed: $BACKUP_DIR"

# 重新启动服务
docker-compose up -d
```

### 3.4 恢复操作

#### 3.4.1 从备份恢复

```bash
#!/bin/bash
BACKUP_DIR="$1"  # 传入备份目录路径

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "Restoring from backup: $BACKUP_DIR"

# 停止服务
docker-compose down

# 恢复数据库
docker run --rm -v superstar2_postgres_data:/pgdata -i alpine tar xzf - -C /pgdata < "$BACKUP_DIR/db.tar.gz"

# 恢复静态文件
tar xzf "$BACKUP_DIR/static.tar.gz" -C data/static/

# 恢复配置
cp "$BACKUP_DIR/env.backup" .env
cp "$BACKUP_DIR/docker-compose.yml.backup" docker-compose.yml

echo "Restore completed. Starting services..."
docker-compose up -d
```

## 4. 监控和告警

### 4.1 应用监控

#### 4.1.1 健康检查端点

- **应用健康**: `GET /health`
- **API文档**: `GET /docs`
- **API状态**: `GET /api/v1/health`

#### 4.1.2 监控脚本

创建监控脚本 `monitor.sh`：

```bash
#!/bin/bash
HEALTH_URL="http://localhost/health"
LOG_FILE="/var/log/superstar_monitor.log"
EMAIL="admin@yourdomain.com"

check_health() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
    
    if [ "$HTTP_CODE" -ne 200 ]; then
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] Application unhealthy (Status: $HTTP_CODE)" >> "$LOG_FILE"
        
        # 发送告警邮件
        echo "Superstar AI application is unhealthy (Status: $HTTP_CODE)" | mail -s "Superstar AI Alert" "$EMAIL"
    fi
}

# 检查服务状态
check_services() {
    STATUS=$(docker-compose ps --format "json" | jq -r 'select(.Status | contains("Exit") or contains("Unhealthy")) | .Service')
    if [ ! -z "$STATUS" ]; then
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TIMESTAMP] Service unhealthy: $STATUS" >> "$LOG_FILE"
        echo "Service unhealthy: $STATUS" | mail -s "Superstar AI Service Alert" "$EMAIL"
    fi
}

check_health
check_services
```

### 4.2 性能监控

#### 4.2.1 资源使用监控

```bash
# 创建资源监控脚本
cat > resource_monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/resource_monitor.log"
THRESHOLD_CPU=80
THRESHOLD_MEM=85

while true; do
    # 获取容器资源使用情况
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}" > /tmp/current_stats
    
    # 检查CPU使用率
    while IFS= read -r line; do
        if [[ $line =~ ([0-9]+)% ]]; then
            usage=${BASH_REMATCH[1]}
            if [ "$usage" -gt "$THRESHOLD_CPU" ]; then
                echo "$(date): High CPU usage detected: $line" >> "$LOG_FILE"
            fi
        fi
    done < <(tail -n +2 /tmp/current_stats | awk '{print $1 "\t" $2}')
    
    # 检查内存使用率
    while IFS= read -r line; do
        if [[ $line =~ ([0-9]+)% ]]; then
            usage=${BASH_REMATCH[1]}
            if [ "$usage" -gt "$THRESHOLD_MEM" ]; then
                echo "$(date): High memory usage detected: $line" >> "$LOG_FILE"
            fi
        fi
    done < <(tail -n +2 /tmp/current_stats | awk '{print $1 "\t" $3}')
    
    sleep 60  # 每分钟检查一次
done
EOF
```

### 4.3 日志分析

#### 4.3.1 日志轮转配置

创建日志轮转配置 `/etc/logrotate.d/superstar`：

```
/var/log/superstar/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
}
```

## 5. 安全运维

### 5.1 安全配置

#### 5.1.1 防火墙配置

```bash
# Ubuntu/Debian
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --reload
```

#### 5.1.2 SSL配置

使用Let's Encrypt获取免费SSL证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 5.2 访问控制

#### 5.2.1 API限流配置

在生产环境中，可以使用Nginx进行限流：

```nginx
# nginx.conf
http {
    # 限制每个IP的连接数
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    # 限制请求频率
    limit_req_zone $binary_remote_addr zone=all:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_conn addr 100;
            limit_req zone=all burst=20 nodelay;
        }
    }
}
```

## 6. 升级和维护

### 6.1 版本升级

#### 6.1.1 代码升级

```bash
# 备份当前版本
./backup.sh

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose build
docker-compose up -d

# 验证升级
curl http://localhost/health
```

#### 6.1.2 数据库迁移

如果有数据库结构变更：

```bash
# 进入后端容器执行迁移
docker-compose exec backend bash
# 在容器内执行
alembic upgrade head
exit
```

### 6.2 滚动更新

对于高可用环境，可以实现滚动更新：

```bash
# 使用标签标记新版本
docker-compose down
git pull origin main
docker-compose build --pull
docker-compose up -d --no-deps backend
# 等待新版本启动完成后再更新其他服务
```

## 7. 故障排查

### 7.1 常见问题

#### 7.1.1 服务无法启动

**症状**: `docker-compose ps` 显示服务状态为 `Exit` 或 `Restarting`

**排查步骤**:
```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs db

# 检查配置文件
docker-compose config

# 检查端口占用
netstat -tulpn | grep :8000
```

#### 7.1.2 数据库连接失败

**症状**: 应用启动时报数据库连接错误

**排查步骤**:
```bash
# 检查数据库服务是否运行
docker-compose ps | grep db

# 检查网络连接
docker-compose exec backend ping db

# 测试数据库连接
docker-compose exec backend python -c "
import sqlalchemy
engine = sqlalchemy.create_engine('postgresql://...')
engine.connect()
"
```

#### 7.1.3 任务队列问题

**症状**: 任务无法处理或处理缓慢

**排查步骤**:
```bash
# 检查Redis和Worker状态
docker-compose ps | grep -E "(redis|worker)"

# 查看Worker日志
docker-compose logs worker

# 检查任务队列长度
docker-compose exec redis redis-cli llen celery
```

### 7.2 诊断工具

#### 7.2.1 一键诊断脚本

创建诊断脚本 `diagnose.sh`：

```bash
#!/bin/bash
echo "=== Superstar AI System Diagnosis ==="
echo "Timestamp: $(date)"
echo ""

echo "1. Service Status:"
docker-compose ps
echo ""

echo "2. Resource Usage:"
docker stats --no-stream
echo ""

echo "3. Recent Logs (last 20 lines):"
echo "--- Backend ---"
docker-compose logs --tail=20 backend
echo ""
echo "--- Worker ---"
docker-compose logs --tail=20 worker
echo ""
echo "--- Redis ---"
docker-compose logs --tail=20 redis
echo ""

echo "4. Health Check:"
curl -s http://localhost/health | jq .
echo ""

echo "5. Database Connection Test:"
docker-compose exec -T backend python -c "
try:
    import asyncio
    from app.core.database import init_db
    asyncio.run(init_db())
    print('✓ Database connection OK')
except Exception as e:
    print('✗ Database connection failed:', e)
"
echo ""

echo "Diagnosis completed."
```

## 8. 性能优化

### 8.1 数据库优化

#### 8.1.1 连接池配置

在 `.env` 中优化数据库连接：

```bash
# 数据库连接池配置
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?max_connections=20&min_connections=5
```

#### 8.1.2 索引优化

定期检查和优化数据库索引：

```sql
-- 检查慢查询
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';

-- 添加必要索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
```

### 8.2 缓存策略

#### 8.2.1 Redis缓存配置

优化Redis配置以提高性能：

```bash
# 在Redis配置中启用
redis.conf:
    maxmemory 2gb
    maxmemory-policy allkeys-lru
    tcp-keepalive 300
```

### 8.3 负载均衡

对于高流量场景，可配置负载均衡：

```nginx
upstream superstar_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://superstar_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 9. 生产环境最佳实践

### 9.1 安全最佳实践

- 使用HTTPS加密所有通信
- 定期轮换密钥和密码
- 限制容器权限
- 定期安全扫描

### 9.2 可靠性最佳实践

- 实现健康检查
- 配置自动重启策略
- 设置资源限制
- 实现监控和告警

### 9.3 性能最佳实践

- 使用连接池
- 实现缓存策略
- 优化数据库查询
- 使用CDN加速静态资源

---

此部署和运维指南提供了Superstar AI项目的完整部署和运维说明，涵盖了从初始部署到日常运维的各个方面。