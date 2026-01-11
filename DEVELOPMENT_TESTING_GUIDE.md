# Superstar AI - 开发和测试指南

## 1. 开发环境设置

### 1.1 本地开发环境

#### 1.1.1 环境要求

- **Python**: 3.8+ (推荐 3.11 或 3.12)
- **Node.js**: 16+ (前端开发)
- **Docker**: 20.10+ (推荐)
- **Docker Compose**: 2.0+
- **Git**: 2.25+

#### 1.1.2 环境搭建

```bash
# 1. 克隆项目
git clone https://github.com/lawye5718/superstar2.git
cd superstar2

# 2. 后端环境设置
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，根据需要修改配置

# 5. 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 1.1.3 前端环境设置

```bash
# 1. 进入前端目录
cd frontend

# 2. 启动前端服务（开发模式）
python -m http.server 8080  # 或使用其他静态文件服务器

# 3. 或使用Node.js
npm install -g serve
serve -s . -l 8080
```

### 1.2 Docker开发环境

```bash
# 使用Docker Compose启动开发环境
docker-compose up --build

# 或单独启动各服务
docker-compose up backend redis worker --build
```

## 2. 代码规范

### 2.1 Python代码规范

#### 2.1.1 代码格式化

```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8 .
mypy .
```

#### 2.1.2 命名规范

- **变量/函数**: `snake_case`
- **类**: `PascalCase`
- **常量**: `UPPER_SNAKE_CASE`
- **私有成员**: `_private_member`

#### 2.1.3 代码风格

```python
# 好的例子
class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            ValueError: 当邮箱已存在时
        """
        if self.email_exists(user_data.email):
            raise ValueError("Email already exists")
        
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password)
        )
        return self.repository.create(user)
    
    def email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        return self.repository.get_by_email(email) is not None
```

### 2.2 前端代码规范

#### 2.2.1 JavaScript规范

- **ES6+语法**: 使用现代JavaScript特性
- **Vue 3 Composition API**: 统一使用Composition API
- **命名**: `camelCase` for variables/functions, `PascalCase` for components

#### 2.2.2 HTML/CSS规范

- **BEM命名法**: Block__Element--Modifier
- **Tailwind CSS**: 使用Tailwind utility classes
- **语义化HTML**: 使用合适的HTML元素

## 3. 项目结构和开发流程

### 3.1 后端开发流程

#### 3.1.1 添加新功能

1. **创建Schema** (`app/schemas/`)
   ```python
   from pydantic import BaseModel
   
   class NewFeatureCreate(BaseModel):
       name: str
       description: str
   ```

2. **创建Model** (`app/models/`)
   ```python
   from sqlalchemy import Column, String, Integer
   from app.core.database import Base
   
   class NewFeature(Base):
       __tablename__ = "new_features"
       
       id = Column(String, primary_key=True)
       name = Column(String, nullable=False)
       description = Column(String)
   ```

3. **创建Service** (`app/services/`)
   ```python
   class NewFeatureService:
       def create_feature(self, db: Session, feature_in: NewFeatureCreate):
           db_feature = NewFeature(**feature_in.dict())
           db.add(db_feature)
           db.commit()
           db.refresh(db_feature)
           return db_feature
   ```

4. **创建API** (`app/api/v1/`)
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from app.core.database import get_sync_db
   
   router = APIRouter()
   
   @router.post("/", response_model=NewFeature)
   def create_new_feature(
       feature: NewFeatureCreate,
       db: Session = Depends(get_sync_db)
   ):
       service = NewFeatureService()
       return service.create_feature(db, feature)
   ```

5. **注册路由** (`app/api/v1/router.py`)
   ```python
   from . import new_feature
   api_router.include_router(new_feature.router, prefix="/new_features", tags=["new_features"])
   ```

### 3.2 前端开发流程

#### 3.2.1 添加新功能

1. **更新状态管理**
   ```javascript
   const newFeatures = ref([]);
   const selectedFeature = ref(null);
   ```

2. **添加API调用**
   ```javascript
   const fetchNewFeatures = async () => {
       try {
           const response = await axios.get(`${API_BASE}/new_features/`);
           newFeatures.value = response.data;
       } catch (error) {
           console.error("Failed to fetch new features:", error);
       }
   };
   ```

3. **创建UI组件**
   ```html
   <div v-for="feature in newFeatures" :key="feature.id" class="feature-card">
       <h3>{{ feature.name }}</h3>
       <p>{{ feature.description }}</p>
   </div>
   ```

## 4. 测试策略

### 4.1 测试分类

#### 4.1.1 单元测试

**测试目标**:
- 独立函数和方法
- 数据验证逻辑
- 业务逻辑处理

**测试框架**: pytest

**示例**:
```python
# test_user_service.py
import pytest
from unittest.mock import Mock
from app.services.user import UserService
from app.schemas.user import UserCreate

def test_create_user_success():
    # Arrange
    user_service = UserService()
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        username="testuser"
    )
    mock_db = Mock()
    
    # Act
    result = user_service.create_user(mock_db, user_data)
    
    # Assert
    assert result.email == "test@example.com"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_create_duplicate_user():
    # Arrange
    user_service = UserService()
    user_data = UserCreate(
        email="existing@example.com",
        password="password123",
        username="existing"
    )
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = Mock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email already registered"):
        user_service.create_user(mock_db, user_data)
```

#### 4.1.2 集成测试

**测试目标**:
- API端点功能
- 数据库交互
- 认证授权

**示例**:
```python
# test_api_endpoints.py
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_create_user_endpoint():
    # Arrange
    user_data = {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "username": "newuser"
    }
    
    # Act
    response = client.post("/api/v1/users/", json=user_data)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"

def test_get_user_with_auth():
    # Arrange
    token = create_access_token(data={"sub": "test-user-id"})
    
    # Act
    response = client.get("/api/v1/users/me", 
                         headers={"Authorization": f"Bearer {token}"})
    
    # Assert
    assert response.status_code == 200
```

#### 4.1.3 端到端测试

**测试目标**:
- 完整用户流程
- 前后端集成
- 用户界面交互

**工具**: Playwright / Selenium

**示例**:
```python
# test_e2e.py
from playwright.sync_api import sync_playwright

def test_user_registration_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to site
        page.goto("http://localhost:8080")
        
        # Click register button
        page.click("text=立即登录")
        
        # Fill registration form
        page.fill("input[type='email']", "test@example.com")
        page.fill("input[type='password']", "password123")
        page.click("text=注册并自动登录")
        
        # Verify registration success
        assert page.is_visible("text=欢迎回来")
        
        browser.close()
```

### 4.2 测试运行

#### 4.2.1 运行测试

```bash
# 运行所有测试
cd backend
pytest

# 运行特定测试文件
pytest tests/test_users.py

# 运行特定测试
pytest tests/test_users.py::test_create_user_success

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行测试并显示详细信息
pytest -v -s
```

#### 4.2.2 测试配置

`pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -ra
    --strict-markers
    --strict-config
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

### 4.3 测试覆盖率

#### 4.3.1 覆盖率要求

- **最小覆盖率**: 80%
- **推荐覆盖率**: 90%+
- **关键业务逻辑**: 100%

#### 4.3.2 覆盖率检查

```bash
# 生成覆盖率报告
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

# 生成HTML报告
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 5. 调试技巧

### 5.1 后端调试

#### 5.1.1 日志调试

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("Function started")
    logger.debug("Processing data: %s", data)
    logger.warning("This is a warning")
    logger.error("An error occurred")
```

#### 5.1.2 调试配置

在 `.env` 中启用调试模式：
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

#### 5.1.3 使用pdb调试

```python
import pdb

def problematic_function():
    # 设置断点
    pdb.set_trace()
    # 代码将在断点处暂停
    result = some_operation()
    return result
```

### 5.2 前端调试

#### 5.2.1 浏览器开发者工具

- **Network标签**: 检查API请求
- **Console标签**: 查看错误信息
- **Elements标签**: 检查DOM结构
- **Sources标签**: 设置断点调试

#### 5.2.2 Vue DevTools

安装Vue DevTools扩展来调试Vue组件状态。

### 5.3 数据库调试

#### 5.3.1 SQLAlchemy日志

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 6. 性能优化

### 6.1 后端性能优化

#### 6.1.1 数据库优化

```python
# 使用selectinload避免N+1查询
from sqlalchemy.orm import selectinload

users = db.query(User).options(selectinload(User.orders)).all()

# 使用索引
from sqlalchemy import Index
Index('idx_user_email', User.email)

# 批量操作
db.bulk_insert_mappings(User, user_dicts)
db.commit()
```

#### 6.1.2 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_expensive_computation(param):
    # 耗时计算
    return result

# Redis缓存
from redis import Redis
redis_client = Redis.from_url(settings.REDIS_URL)

def get_cached_data(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    data = compute_expensive_operation()
    redis_client.setex(key, 3600, json.dumps(data))
    return data
```

### 6.2 前端性能优化

#### 6.2.1 图片优化

```javascript
// 懒加载
const lazyLoadImages = () => {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
};
```

#### 6.2.2 API请求优化

```javascript
// 请求防抖
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

const debouncedSearch = debounce(async (query) => {
    const results = await searchAPI(query);
    updateResults(results);
}, 300);
```

## 7. 开发最佳实践

### 7.1 代码质量

#### 7.1.1 代码审查清单

- [ ] 代码符合项目规范
- [ ] 添加了适当的单元测试
- [ ] 文档完整（函数注释、类注释）
- [ ] 错误处理完善
- [ ] 性能影响评估
- [ ] 安全性检查

#### 7.1.2 提交信息规范

使用约定式提交格式：

```
<type>(<scope>): <short summary>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 7.2 分支管理

#### 7.2.1 分支策略

```
main (生产分支)
├── develop (开发分支)
├── feature/* (功能分支)
├── release/* (发布分支)
└── hotfix/* (紧急修复分支)
```

#### 7.2.2 工作流程

```bash
# 创建功能分支
git checkout -b feature/new-feature develop

# 开发完成后
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 创建PR合并到develop
# 代码审查通过后合并
```

### 7.3 依赖管理

#### 7.3.1 Python依赖

- 使用虚拟环境隔离依赖
- 定期更新依赖包
- 使用依赖锁定文件

```bash
# 更新依赖
pip install --upgrade package_name

# 生成新的requirements.txt
pip freeze > requirements.txt

# 安全扫描
pip install safety
safety check
```

## 8. 测试驱动开发 (TDD)

### 8.1 TDD流程

1. **编写失败测试**: 先编写测试用例，确保它失败
2. **编写最简单的代码**: 让测试通过
3. **重构**: 改进代码质量，确保测试仍通过
4. **重复**: 为下一个功能点重复此过程

### 8.2 示例

```python
# 1. 先写测试
def test_calculate_discount():
    # Arrange
    price = 100
    discount_percent = 10
    
    # Act
    result = calculate_discount(price, discount_percent)
    
    # Assert
    assert result == 90  # 100 - 10% = 90

# 2. 再写实现
def calculate_discount(price: float, discount_percent: float) -> float:
    """计算折扣后价格"""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percent must be between 0 and 100")
    
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount

# 3. 重构（如有必要）
```

## 9. CI/CD集成

### 9.1 GitHub Actions示例

`.github/workflows/test.yml`:
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### 9.2 代码质量检查

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install tools
      run: pip install black flake8 mypy
    - name: Check formatting
      run: black --check .
    - name: Check linting
      run: flake8 .
    - name: Type checking
      run: mypy .
```

## 10. 本地开发最佳实践

### 10.1 环境隔离

- 为每个项目使用独立的虚拟环境
- 使用不同的端口避免冲突
- 配置独立的数据库实例

### 10.2 调试工具

#### 10.2.1 IDE配置

推荐IDE及其插件：
- **VS Code**: Python extension, Pylance, Black Formatter
- **PyCharm**: 内置Python支持，Docker集成
- **Vim/Neovim**: Python插件，LSP支持

#### 10.2.2 开发工具

```bash
# API测试
pip install httpie
# 使用示例: http :8000/api/v1/users/

# 数据库客户端
pip install ipython
# 使用示例: ipython -i scripts/db_shell.py

# 任务运行器
pip install invoke
# 创建tasks.py定义常用开发任务
```

### 10.3 本地开发脚本

创建 `scripts/dev_setup.py`:

```python
#!/usr/bin/env python
"""
开发环境快速设置脚本
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, desc=""):
    """运行命令并显示进度"""
    print(f"[+] {desc}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[-] 命令失败: {cmd}")
        sys.exit(1)
    return result

def setup_dev_environment():
    """设置开发环境"""
    print("[*] 开始设置开发环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print("[-] Python版本过低，需要3.8+")
        sys.exit(1)
    
    # 创建虚拟环境
    if not Path("venv").exists():
        run_command("python -m venv venv", "创建虚拟环境")
    
    # 激活虚拟环境并安装依赖
    if sys.platform.startswith("win"):
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    run_command(f"{pip_cmd} install -r backend/requirements.txt", "安装依赖")
    
    # 检查环境变量
    if not Path(".env").exists():
        run_command("cp backend/.env.example .env", "创建环境变量文件")
        print("[!] 请编辑 .env 文件配置环境变量")
    
    print("[*] 开发环境设置完成!")
    print("[*] 运行以下命令启动开发服务器:")
    print("   source venv/bin/activate && cd backend && uvicorn app.main:app --reload")

if __name__ == "__main__":
    setup_dev_environment()
```

---

此开发和测试指南提供了Superstar AI项目的完整开发和测试流程说明，帮助开发人员高效地进行开发、测试和调试工作。