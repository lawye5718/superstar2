# Superstar AI - 测试指南

## 项目概述
本项目是一个AI生成照片的平台，用户可以选择不同的模板（风格）来生成自己的写真照片。管理员可以上架新的模板。

## 已修复的问题

### 1. 🔧 语法错误修复
- **问题**: `backend/app/main.py` 第110行存在未闭合的三引号字符串
- **修复**: 正确闭合字符串

### 2. 🗄️ 数据库模型完善
- **问题**: User模型缺少必要字段
- **修复**: 添加了 `face_image_url` 和 `gender` 字段

### 3. 🔐 认证系统实现
- **问题**: 缺少登录/注册功能
- **修复**: 
  - 创建了 `auth.py` 路由
  - 实现 POST /api/v1/auth/login
  - 实现 POST /api/v1/auth/register
  - 添加JWT token认证机制

### 4. 💰 充值功能实现
- **问题**: 用户无法充值
- **修复**: 
  - 添加 POST /api/v1/users/top-up 端点
  - 前端添加充值模态框

### 5. 📊 Schema修复
- **问题**: TemplateResponse 和 OrderResponse 缺少必要字段
- **修复**: 
  - TemplateResponse 添加 price 和 usage_count
  - OrderResponse 添加 template_id, result_image_url, status

### 6. 👨‍💼 管理员功能完善
- **问题**: 缺少管理员用户管理功能
- **修复**:
  - 添加 /api/v1/admin/users 端点
  - 添加 /api/v1/admin/users/role 端点
  - 添加 /api/v1/admin/stats 端点
  - 创建管理员用户创建脚本

### 7. 📱 前端界面优化
- **问题**: 缺少登录界面，余额显示错误
- **修复**:
  - 添加登录/注册模态框
  - 实现JWT token本地存储
  - 修正余额显示（credits vs balance）
  - 添加充值界面
  - 添加管理员权限判断

## 测试账号

### 普通用户
- **邮箱**: demo@example.com
- **密码**: default_password
- **初始积分**: 100

### 管理员
- **邮箱**: admin@example.com
- **密码**: admin123
- **初始积分**: 1000

## 测试流程

### 一、管理员流程测试

#### 1. 管理员登录
1. 打开前端页面（http://localhost:8000 或 frontend/index.html）
2. 点击"登录/注册"按钮
3. 输入管理员账号：admin@example.com / admin123
4. 点击"登录"
5. **预期结果**: 
   - 成功登录
   - 导航栏显示管理员入口（Ops按钮）
   - 显示余额：1000积分

#### 2. 管理员上架模板
1. 登录后，点击导航栏的"Ops"按钮
2. 进入管理员后台界面
3. 上传样图（点击"1. 样图上传"）
4. 填写基本信息：
   - 标题：例如"古风写真"
   - 分类：选择分类（复古、轻奢、运动、森系、职场）
   - 价格：设置价格（例如15积分）
5. 配置Prompt：
   - Base Prompt: "High quality, 8k resolution, professional photography"
   - Variable Prompt: "traditional chinese style, hanfu dress"
   - Negative Prompt: "nsfw, low quality, bad anatomy"
6. 点击"🚀 上架新模版"
7. **预期结果**:
   - 提示"✅ 上架成功！"
   - 在画廊中可以看到新上架的模板

#### 3. 查看用户列表（需要API调用）
使用API客户端（如Postman）测试：
```bash
curl -H "Authorization: Bearer {admin_token}" \
  http://localhost:8000/api/v1/admin/users
```
**预期结果**: 返回用户列表

#### 4. 查看统计信息
```bash
curl -H "Authorization: Bearer {admin_token}" \
  http://localhost:8000/api/v1/admin/stats
```
**预期结果**: 返回系统统计数据（用户数、订单数等）

### 二、用户流程测试

#### 1. 用户注册
1. 打开前端页面
2. 点击"登录/注册"按钮
3. 点击"没有账号？点击注册"
4. 输入新邮箱和密码
5. 点击"注册"
6. **预期结果**:
   - 注册成功
   - 自动登录
   - 显示余额：100积分（新用户赠送）

#### 2. 上传头像
1. 登录后，点击导航栏的"👤 余额: 100"
2. 在档案模态框中：
   - 选择头像文件
   - 选择性别
   - 点击"保存档案"
3. **预期结果**:
   - 上传成功
   - 显示上传的头像

#### 3. 浏览模板（相机模式）
1. 确保在"复古相机"视图
2. 点击快门按钮（红色圆形按钮）
3. **预期结果**:
   - 随机显示一个模板
   - 显示模板标题和图片
   - 显示"我也要同款"按钮和价格

#### 4. 浏览模板（画廊模式）
1. 点击导航栏的"画廊套餐"
2. 浏览不同分类的模板
3. 点击分类标签过滤
4. **预期结果**:
   - 显示所有已上架的模板
   - 可以按分类筛选
   - 鼠标悬停显示详情

#### 5. 充值积分
1. 点击导航栏的"👤 余额"
2. 在档案模态框中点击"💰 充值"
3. 选择充值金额或输入自定义金额
4. 点击"充值 XX 积分"
5. **预期结果**:
   - 充值成功
   - 余额增加

#### 6. 创建订单（生成照片）
1. 在相机模式或画廊模式选择一个模板
2. 点击"我也要同款"或直接点击模板
3. 确认消耗积分
4. **预期结果**:
   - 如果未上传头像，提示先上传
   - 如果余额不足，提示充值
   - 订单创建成功后显示处理进度
   - 处理完成后显示结果图片
   - 可以下载原图

#### 7. 查看订单历史（需要API调用）
```bash
curl -H "Authorization: Bearer {user_token}" \
  http://localhost:8000/api/v1/users/orders
```
**预期结果**: 返回用户的订单历史

#### 8. 退出登录
1. 点击导航栏的"退出"按钮
2. **预期结果**:
   - 退出成功
   - 返回登录界面

## API端点测试

### 认证 API
- POST /api/v1/auth/login - 登录
- POST /api/v1/auth/register - 注册

### 用户 API
- GET /api/v1/users/me - 获取当前用户
- POST /api/v1/users/face - 上传头像
- POST /api/v1/users/top-up - 充值
- GET /api/v1/users/orders - 订单历史

### 模板 API
- GET /api/v1/templates - 获取模板列表
- GET /api/v1/templates/random - 随机模板

### 订单 API
- POST /api/v1/orders - 创建订单
- GET /api/v1/orders/{id} - 查询订单

### 管理员 API
- POST /api/v1/admin/templates - 上架模板
- GET /api/v1/admin/users - 用户列表
- POST /api/v1/admin/users/role - 更新用户角色
- GET /api/v1/admin/stats - 统计信息

## 已知限制和待改进项

### 当前实现的简化处理：
1. **AI生成模拟**: 订单创建后立即返回模板的封面图作为结果，实际应该调用AI服务
2. **支付系统**: 充值功能是模拟的，实际应该接入支付网关
3. **文件存储**: 上传的文件存储在本地，生产环境应使用云存储
4. **异步任务**: 订单处理应该使用Celery等异步任务队列

### 待添加功能：
1. 前端订单历史查看界面
2. 前端管理员统计面板
3. 用户行为分析和推荐系统
4. 更完善的错误处理
5. 图片水印和版权保护

## 运行方法

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端
直接打开 `frontend/index.html` 或通过后端访问 `http://localhost:8000`

## 数据库
使用SQLite数据库（superstar.db），位于backend目录下。
首次启动会自动创建表和示例数据。

## 创建管理员账号
```bash
cd backend
PYTHONPATH=. python scripts/create_admin.py
```

## 测试API
可以使用 FastAPI 自动生成的文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
