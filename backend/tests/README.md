# Testing Guide

## 运行测试

### 安装测试依赖
```bash
cd backend
pip install -r requirements-test.txt
```

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_api.py
```

### 运行特定测试类
```bash
pytest tests/test_api.py::TestAuthEndpoints
```

### 运行特定测试函数
```bash
pytest tests/test_api.py::TestAuthEndpoints::test_login_success
```

### 查看测试覆盖率
```bash
pytest --cov=app --cov-report=html
# 在浏览器中打开 htmlcov/index.html
```

### 运行测试并显示详细输出
```bash
pytest -v -s
```

## 测试结构

```
tests/
├── conftest.py           # 测试配置和fixtures
├── test_api.py          # API端点测试
├── test_models.py       # 数据模型测试（待添加）
├── test_services.py     # 服务层测试（待添加）
└── test_security.py     # 安全测试（待添加）
```

## 测试覆盖范围

### 已实现的测试
- ✅ 健康检查端点
- ✅ 用户认证（登录）
- ✅ 用户注册
- ✅ 密码强度验证
- ✅ 邮箱格式验证
- ✅ 订单创建验证
- ✅ UUID格式验证

### 待添加的测试
- [ ] 模板CRUD操作
- [ ] 订单完整流程
- [ ] 文件上传验证
- [ ] 权限控制测试
- [ ] 并发订单测试
- [ ] 数据库事务测试
- [ ] Celery任务测试
- [ ] 性能测试

## Fixtures说明

### `test_db`
提供一个独立的测试数据库，每个测试后自动清理。

### `client`
提供FastAPI测试客户端，已配置测试数据库。

### `test_user`
创建一个普通测试用户。

### `admin_user`
创建一个管理员测试用户。

### `auth_token`
获取普通用户的JWT认证令牌。

### `admin_token`
获取管理员的JWT认证令牌。

## 编写测试的最佳实践

### 1. 测试命名
```python
def test_should_return_200_when_valid_credentials():
    """测试名称应清晰描述测试的目的"""
    pass
```

### 2. 使用Fixtures
```python
def test_create_order(client, auth_token, test_user):
    """使用fixtures简化测试设置"""
    response = client.post(
        "/api/v1/orders/",
        json={"template_id": "uuid-here"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

### 3. 测试边界条件
```python
def test_password_validation():
    # 测试各种无效输入
    test_cases = [
        ("short", "太短"),
        ("nouppercase123", "无大写"),
        ("NoNumber", "无数字"),
        ("", "空字符串"),
    ]
    for password, reason in test_cases:
        # 测试每个情况
        pass
```

### 4. 独立的测试
每个测试应该是独立的，不依赖其他测试的执行顺序。

### 5. 清理资源
使用fixtures的teardown或try/finally确保资源被正确清理。

## 持续集成

### GitHub Actions示例
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest
```

## 调试测试

### 进入调试器
```python
def test_something():
    import pdb; pdb.set_trace()
    # 测试代码
```

### 查看详细日志
```bash
pytest -v -s --log-cli-level=DEBUG
```

### 只运行失败的测试
```bash
pytest --lf  # last-failed
```

### 在第一个失败时停止
```bash
pytest -x
```
