# Superstar AI API 文档

## 1. 概述

Superstar AI API 是一个 RESTful API，用于管理用户、模板、订单、画廊和生成任务。API 使用 JSON 格式进行数据交换，通过 HTTP 状态码表示操作结果。

### 1.1 基础 URL

生产环境: `https://api.superstar.ai/v1/`  
开发环境: `http://localhost:8000/api/v1/`

### 1.2 认证

大多数 API 端点需要用户认证。认证通过在请求头中添加 `Authorization` 字段实现：

```
Authorization: Bearer <JWT_TOKEN>
```

### 1.3 内容类型

所有请求和响应的 `Content-Type` 都是 `application/json`。

### 1.4 HTTP 状态码

- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求数据无效
- `401 Unauthorized` - 未认证或认证失败
- `403 Forbidden` - 无权限访问
- `404 Not Found` - 资源不存在
- `422 Unprocessable Entity` - 请求数据验证失败
- `500 Internal Server Error` - 服务器内部错误

## 2. 用户 API

### 2.1 创建用户

创建新用户账户。

```
POST /users/
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "balance": 0.0,
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**参数:**
- `email` (string, required): 用户邮箱地址
- `password` (string, required): 用户密码（至少8位）

### 2.2 获取用户信息

获取当前认证用户的信息。

```
GET /users/me
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "user123",
  "balance": 50.0,
  "face_image_url": "http://localhost:8000/static/uploads/user_face.jpg",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 2.3 更新用户头像

上传并更新用户的基准头像。

```
POST /users/face
```

**表单数据:**
- `file` (file, required): 图像文件
- `gender` (string, optional): 性别 ("male"|"female"|"unisex", default: "female")

**响应:**
```json
{
  "url": "http://localhost:8000/static/uploads/user_face.jpg"
}
```

### 2.4 用户充值

为用户账户充值。

```
POST /users/topup
```

**请求体:**
```json
{
  "amount": 100
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "balance": 150.0,
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## 3. 模板 API

### 3.1 获取模板列表

获取所有可用模板。

```
GET /templates/
```

**查询参数:**
- `category` (string, optional): 按类别过滤模板

**响应:**
```json
[
  {
    "id": "template-uuid",
    "title": "复古胶片风格",
    "category": "复古",
    "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
    "price": 9.9,
    "usage_count": 125,
    "created_at": "2023-01-01T00:00:00Z"
  }
]
```

### 3.2 获取随机模板

获取一个随机模板。

```
GET /templates/random
```

**响应:**
```json
{
  "id": "template-uuid",
  "title": "复古胶片风格",
  "category": "复古",
  "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
  "price": 9.9,
  "usage_count": 125,
  "created_at": "2023-01-01T00:00:00Z"
}
```

## 4. 订单 API

### 4.1 创建订单

创建新的图像生成订单。

```
POST /orders/
```

**请求体:**
```json
{
  "template_id": "template-uuid"
}
```

**响应:**
```json
{
  "id": "order-uuid",
  "user_id": "user-uuid",
  "template_id": "template-uuid",
  "status": "PENDING",
  "amount": 9.9,
  "result_image_url": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 4.2 获取订单详情

获取特定订单的详细信息。

```
GET /orders/{order_id}
```

**路径参数:**
- `order_id` (string, required): 订单UUID

**响应:**
```json
{
  "id": "order-uuid",
  "user_id": "user-uuid",
  "template_id": "template-uuid",
  "status": "COMPLETED",
  "amount": 9.9,
  "result_image_url": "http://localhost:8000/static/uploads/result_image.jpg",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:30Z"
}
```

### 4.3 获取用户订单列表

获取当前用户的订单列表。

```
GET /orders/
```

**响应:**
```json
[
  {
    "id": "order-uuid",
    "user_id": "user-uuid",
    "template_id": "template-uuid",
    "status": "COMPLETED",
    "amount": 9.9,
    "result_image_url": "http://localhost:8000/static/uploads/result_image.jpg",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:30Z"
  }
]
```

## 5. 管理员 API

### 5.1 模板管理

#### 5.1.1 创建模板

管理员创建新模板。

```
POST /admin/templates/
```

**请求体:**
```json
{
  "title": "新模板标题",
  "category": "风格类别",
  "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
  "price": 19.9,
  "prompt_config": {
    "base_prompt": "base prompt text",
    "variable_prompt": "variable prompt text",
    "negative_prompt": "negative prompt text"
  }
}
```

**响应:**
```json
{
  "id": "template-uuid",
  "title": "新模板标题",
  "category": "风格类别",
  "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
  "price": 19.9,
  "usage_count": 0,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 5.1.2 删除模板

管理员删除模板。

```
DELETE /admin/templates/{id}
```

**路径参数:**
- `id` (string, required): 模板UUID

**响应:**
```json
{
  "status": "success",
  "message": "Template deleted"
}
```

### 5.2 用户管理

#### 5.2.1 获取用户列表

获取所有用户列表。

```
GET /admin/users
```

**查询参数:**
- `skip` (integer, optional): 跳过的记录数，默认0
- `limit` (integer, optional): 返回的最大记录数，默认50

**响应:**
```json
{
  "total": 10,
  "items": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "username": "username",
      "balance": 50.0,
      "is_active": true,
      "is_superuser": false,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### 5.3 数据看板

#### 5.3.1 获取运营数据

获取实时运营数据看板。

```
GET /admin/stats/dashboard
```

**响应:**
```json
{
  "total_users": 125,
  "total_revenue": 2500.0,
  "total_orders": 350,
  "total_templates": 25
}
```

## 6. 工具 API

### 6.1 文件上传

通用文件上传接口。

```
POST /utils/upload
```

**表单数据:**
- `file` (file, required): 要上传的文件

**响应:**
```json
{
  "url": "http://localhost:8000/static/uploads/filename.jpg"
}
```

## 7. 认证 API

### 7.1 用户登录

获取JWT访问令牌。

```
POST /auth/login/access-token
Content-Type: application/x-www-form-urlencoded
```

**表单数据:**
- `username` (string, required): 用户邮箱
- `password` (string, required): 用户密码

**响应:**
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer"
}
```

## 8. 健康检查

### 8.1 健康检查端点

检查应用程序健康状态。

```
GET /health
```

**响应:**
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

## 9. 错误处理

API 使用标准HTTP状态码和一致的错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

## 10. 速率限制

为防止滥用，某些端点实施了速率限制：

- 文件上传: 10次/分钟
- 认证相关: 5次/分钟
- 其他端点: 60次/分钟