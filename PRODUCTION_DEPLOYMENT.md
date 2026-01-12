# 生产环境部署指南 (Production Deployment Guide)

## 📋 部署前检查清单

### 1. 环境配置 (必须完成)

#### 1.1 密钥配置
```bash
# 生成强随机密钥
openssl rand -hex 32

# 在生产环境.env文件中设置
SECRET_KEY=<生成的密钥>
```

#### 1.2 数据库配置
```bash
# PostgreSQL生产配置
DATABASE_URL=postgresql://username:strong_password@hostname:5432/database_name

# 确保数据库已创建
psql -U postgres -c "CREATE DATABASE superstar_production;"
```

#### 1.3 Redis配置
```bash
# Redis连接URL
REDIS_URL=redis://redis_host:6379/0

# 如果使用密码
REDIS_URL=redis://:password@redis_host:6379/0
```

#### 1.4 CORS配置
```bash
# 仅允许受信任的域名
CORS_ORIGINS=https://app.superstar.ai,https://www.superstar.ai
```

#### 1.5 第三方服务
```bash
# 火山引擎AI服务
VOLC_API_KEY=your_api_key
VOLC_SECRET_KEY=your_secret_key

# 腾讯云COS
COS_SECRET_ID=your_secret_id
COS_SECRET_KEY=your_secret_key
COS_REGION=ap-beijing
COS_BUCKET=your-bucket-name
```

### 2. 安全配置

#### 2.1 移除开发模式配置
- [ ] 确认SECRET_KEY已更改
- [ ] 确认CORS不包含"*"
- [ ] 确认数据库密码强度
- [ ] 检查日志级别（INFO或WARNING）
- [ ] 禁用调试模式

#### 2.2 网络安全
- [ ] 配置防火墙规则
- [ ] 仅开放必要端口（80, 443）
- [ ] 配置SSL/TLS证书
- [ ] 使用HTTPS
- [ ] 配置反向代理（Nginx/Traefik）

#### 2.3 数据库安全
- [ ] 使用强密码
- [ ] 限制数据库访问IP
- [ ] 启用SSL连接
- [ ] 配置定期备份
- [ ] 设置连接池限制

## 🚀 Docker部署步骤

### 方法一：使用Docker Compose（推荐）

#### 1. 准备环境文件
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，设置生产环境变量
vim .env
```

#### 2. 构建并启动服务
```bash
# 构建镜像
docker-compose build

# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f worker
```

#### 3. 初始化数据库
```bash
# 数据库会在容器启动时自动初始化
# 检查初始化日志
docker-compose logs backend | grep "init"
```

#### 4. 验证部署
```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试API
curl http://localhost:8000/

# 测试前端
curl http://localhost:8080/
```

### 方法二：独立部署

#### 1. 部署数据库
```bash
# 使用托管PostgreSQL服务（推荐）
# 或自行部署：
docker run -d \
  --name superstar-db \
  -e POSTGRES_USER=superstar \
  -e POSTGRES_PASSWORD=<strong_password> \
  -e POSTGRES_DB=superstar \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine
```

#### 2. 部署Redis
```bash
docker run -d \
  --name superstar-redis \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:alpine
```

#### 3. 部署后端API
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
python scripts/init_data.py

# 使用Gunicorn运行（生产推荐）
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

#### 4. 部署Celery Worker
```bash
# 在单独的进程中运行
celery -A app.tasks.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=1000
```

## 🔧 Nginx反向代理配置

### 配置示例
```nginx
# /etc/nginx/sites-available/superstar.conf

upstream backend_api {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:8080;
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name superstar.ai www.superstar.ai;
    return 301 https://$server_name$request_uri;
}

# HTTPS主站
server {
    listen 443 ssl http2;
    server_name superstar.ai www.superstar.ai;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/superstar.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/superstar.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 前端
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 上传文件大小限制
        client_max_body_size 10M;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件
    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 启用配置
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/superstar.conf /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## 📊 监控和日志

### 1. 应用日志
```bash
# 查看后端日志
docker-compose logs -f backend

# 查看Worker日志
docker-compose logs -f worker

# 查看最近100行
docker-compose logs --tail=100 backend
```

### 2. 健康监控
```bash
# 设置健康检查脚本
#!/bin/bash
# health_check.sh

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $STATUS -ne 200 ]; then
    echo "Health check failed with status: $STATUS"
    # 发送告警通知
    exit 1
fi
echo "Health check passed"
```

### 3. 性能监控工具
- **APM**: New Relic, Datadog, 或 Sentry
- **日志聚合**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **指标监控**: Prometheus + Grafana

## 🔄 数据库备份

### 自动备份脚本
```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backup/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="superstar"

# 创建备份
docker exec superstar_db pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 保留最近30天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

### 设置定时任务
```bash
# 编辑crontab
crontab -e

# 每天凌晨2点执行备份
0 2 * * * /path/to/backup_db.sh >> /var/log/backup.log 2>&1
```

## 🔥 故障排查

### 常见问题

#### 1. 应用无法启动
```bash
# 检查日志
docker-compose logs backend

# 检查环境变量
docker-compose exec backend env | grep DATABASE_URL

# 验证数据库连接
docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

#### 2. 数据库连接失败
```bash
# 检查PostgreSQL是否运行
docker-compose ps db

# 测试数据库连接
docker-compose exec db psql -U postgres -c "SELECT 1"

# 检查网络连通性
docker-compose exec backend ping db
```

#### 3. Worker任务不执行
```bash
# 检查Redis连接
docker-compose exec worker redis-cli -h redis ping

# 查看Celery Worker状态
docker-compose exec worker celery -A app.tasks.celery_app status

# 手动测试任务
docker-compose exec worker python -c "from app.tasks import generate_image_task; print(generate_image_task)"
```

## 📈 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_templates_gender ON prompts(gender);
CREATE INDEX idx_templates_approved ON prompts(is_approved);

-- 分析表统计信息
ANALYZE users;
ANALYZE orders;
ANALYZE prompts;
```

### 2. 连接池配置
```python
# 在 app/core/database.py 中
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=10,       # 最大溢出连接
    pool_pre_ping=True,    # 连接前检查
    pool_recycle=3600,     # 1小时回收连接
)
```

### 3. Redis缓存
```python
# 缓存热门模板
from redis import Redis
redis_client = Redis.from_url(settings.REDIS_URL)

def get_popular_templates():
    # 尝试从缓存获取
    cached = redis_client.get('popular_templates')
    if cached:
        return json.loads(cached)
    
    # 从数据库查询
    templates = db.query(Template).order_by(Template.usage_count.desc()).limit(10).all()
    
    # 缓存结果（5分钟）
    redis_client.setex('popular_templates', 300, json.dumps(templates))
    return templates
```

## 🔐 安全加固

### 1. 定期更新
```bash
# 更新系统包
apt update && apt upgrade -y

# 更新Docker镜像
docker-compose pull
docker-compose up -d

# 更新Python依赖
pip install --upgrade -r requirements.txt
```

### 2. 安全扫描
```bash
# 扫描Docker镜像漏洞
docker scan superstar_backend:latest

# 扫描Python依赖漏洞
pip install safety
safety check
```

### 3. 访问控制
```bash
# 限制数据库访问
# PostgreSQL配置文件 pg_hba.conf
host    superstar    superstar    10.0.0.0/8    md5

# 使用防火墙限制端口
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 5432/tcp  # 不对外开放数据库
ufw enable
```

## 📞 运维支持

### 紧急联系
- **技术负责人**: admin@superstar.ai
- **运维团队**: ops@superstar.ai

### 运维文档
- API文档: https://api.superstar.ai/docs
- 监控面板: https://monitor.superstar.ai
- 日志平台: https://logs.superstar.ai

## 🎯 检查清单总结

部署前请确认：
- [x] 所有环境变量已配置
- [x] 数据库已初始化
- [x] SSL证书已配置
- [x] 备份策略已建立
- [x] 监控已设置
- [x] 日志已配置
- [x] 安全扫描已完成
- [x] 性能测试已通过
- [x] 回滚方案已准备

**部署成功后，建议在低流量时段进行灰度发布，逐步放量！**
