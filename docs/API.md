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
  "credits": 0,
  "roles": ["user"],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**参数:**
- `email` (string, required): 用户邮箱地址
- `password` (string, required): 用户密码（至少8位）

### 2.2 获取用户信息

根据用户ID获取用户信息。

```
GET /users/{user_id}
```

**路径参数:**
- `user_id` (string, required): 用户UUID

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "credits": 100,
  "roles": ["user"],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 2.3 更新用户信息

更新用户信息。

```
PUT /users/{user_id}
```

**路径参数:**
- `user_id` (string, required): 用户UUID

**请求体:**
```json
{
  "email": "newemail@example.com",
  "credits": 150
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newemail@example.com",
  "credits": 150,
  "roles": ["user"],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

### 2.4 删除用户

删除用户账户。

```
DELETE /users/{user_id}
```

**路径参数:**
- `user_id` (string, required): 用户UUID

**响应:**
```json
{
  "message": "User deleted successfully"
}
```

## 3. 模板 API

### 3.1 创建模板

创建新的生成模板。

```
POST /templates/
```

**请求体:**
```json
{
  "title": "复古风格写真",
  "gender": "Female",
  "tags": ["复古", "大衣", "冬季"],
  "config": {
    "base_prompt": "High quality, 8k resolution, masterpiece",
    "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
    "negative_prompt": "bad anatomy"
  },
  "is_approved": true,
  "display_image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "复古风格写真",
  "gender": "Female",
  "tags": ["复古", "大衣", "冬季"],
  "config": {
    "base_prompt": "High quality, 8k resolution, masterpiece",
    "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
    "negative_prompt": "bad anatomy"
  },
  "is_approved": true,
  "display_image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 3.2 获取模板列表

获取模板列表，支持分页。

```
GET /templates/
```

**查询参数:**
- `skip` (integer, optional): 跳过的记录数，默认为0
- `limit` (integer, optional): 返回的记录数，默认为100

**响应:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "复古风格写真",
    "gender": "Female",
    "tags": ["复古", "大衣", "冬季"],
    "config": {
      "base_prompt": "High quality, 8k resolution, masterpiece",
      "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
      "negative_prompt": "bad anatomy"
    },
    "is_approved": true,
    "display_image_urls": [
      "https://example.com/image1.jpg"
    ],
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

### 3.3 获取模板详情

根据模板ID获取模板详情。

```
GET /templates/{template_id}
```

**路径参数:**
- `template_id` (string, required): 模板UUID

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "复古风格写真",
  "gender": "Female",
  "tags": ["复古", "大衣", "冬季"],
  "config": {
    "base_prompt": "High quality, 8k resolution, masterpiece",
    "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
    "negative_prompt": "bad anatomy"
  },
  "is_approved": true,
  "display_image_urls": [
    "https://example.com/image1.jpg"
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 3.4 更新模板

更新模板信息。

```
PUT /templates/{template_id}
```

**路径参数:**
- `template_id` (string, required): 模板UUID

**请求体:**
```json
{
  "title": "更新后的复古风格写真",
  "is_approved": false
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "更新后的复古风格写真",
  "gender": "Female",
  "tags": ["复古", "大衣", "冬季"],
  "config": {
    "base_prompt": "High quality, 8k resolution, masterpiece",
    "variable_prompt": "wearing green wool vintage coat, brown textured wall background",
    "negative_prompt": "bad anatomy"
  },
  "is_approved": false,
  "display_image_urls": [
    "https://example.com/image1.jpg"
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

### 3.5 删除模板

删除模板。

```
DELETE /templates/{template_id}
```

**路径参数:**
- `template_id` (string, required): 模板UUID

**响应:**
```json
{
  "message": "Template deleted successfully"
}
```

## 4. 订单 API

### 4.1 创建订单

创建新订单。

```
POST /orders/
```

**请求体:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "credits_purchased": 10,
  "amount": 99.00,
  "platform": "web",
  "status": "PENDING"
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "credits_purchased": 10,
  "amount": 99.00,
  "platform": "web",
  "status": "PENDING",
  "transaction_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 4.2 获取订单列表

获取订单列表，支持分页。

```
GET /orders/
```

**查询参数:**
- `skip` (integer, optional): 跳过的记录数，默认为0
- `limit` (integer, optional): 返回的记录数，默认为100

**响应:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "credits_purchased": 10,
    "amount": 99.00,
    "platform": "web",
    "status": "PENDING",
    "transaction_id": null,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

### 4.3 获取订单详情

根据订单ID获取订单详情。

```
GET /orders/{order_id}
```

**路径参数:**
- `order_id` (string, required): 订单UUID

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "credits_purchased": 10,
  "amount": 99.00,
  "platform": "web",
  "status": "PENDING",
  "transaction_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## 5. 画廊 API

### 5.1 创建画廊项目

创建新的画廊项目。

```
POST /galleries/
```

**请求体:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "image_url_free": "https://example.com/free_image.jpg",
  "image_url_paid": "https://example.com/paid_image.jpg",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "is_public": true
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "image_url_free": "https://example.com/free_image.jpg",
  "image_url_paid": "https://example.com/paid_image.jpg",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "is_public": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### 5.2 获取画廊列表

获取画廊列表，支持分页。

```
GET /galleries/
```

**查询参数:**
- `skip` (integer, optional): 跳过的记录数，默认为0
- `limit` (integer, optional): 返回的记录数，默认为100

**响应:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "template_id": "550e8400-e29b-41d4-a716-446655440001",
    "image_url_free": "https://example.com/free_image.jpg",
    "image_url_paid": "https://example.com/paid_image.jpg",
    "thumbnail_url": "https://example.com/thumbnail.jpg",
    "is_public": true,
    "created_at": "2023-01-01T00:00:00Z"
  }
]
```

### 5.3 获取画廊详情

根据画廊ID获取画廊详情。

```
GET /galleries/{gallery_id}
```

**路径参数:**
- `gallery_id` (string, required): 画廊UUID

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "image_url_free": "https://example.com/free_image.jpg",
  "image_url_paid": "https://example.com/paid_image.jpg",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "is_public": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

## 6. 任务 API

### 6.1 创建生成任务

创建新的AI图像生成任务。

```
POST /tasks/
```

**请求体:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "PENDING",
  "portrait_url": "https://example.com/portrait.jpg",
  "error_message": null
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "PENDING",
  "portrait_url": "https://example.com/portrait.jpg",
  "error_message": null,
  "result_gallery_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 6.2 获取任务列表

获取任务列表，支持分页。

```
GET /tasks/
```

**查询参数:**
- `skip` (integer, optional): 跳过的记录数，默认为0
- `limit` (integer, optional): 返回的记录数，默认为100

**响应:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "template_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "PENDING",
    "portrait_url": "https://example.com/portrait.jpg",
    "error_message": null,
    "result_gallery_id": null,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

### 6.3 获取任务详情

根据任务ID获取任务详情。

```
GET /tasks/{task_id}
```

**路径参数:**
- `task_id` (string, required): 任务UUID

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "COMPLETED",
  "portrait_url": "https://example.com/portrait.jpg",
  "error_message": null,
  "result_gallery_id": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:30:00Z"
}
```

### 6.4 更新任务

更新任务信息。

```
PUT /tasks/{task_id}
```

**路径参数:**
- `task_id` (string, required): 任务UUID

**请求体:**
```json
{
  "status": "PROCESSING",
  "error_message": null
}
```

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "PROCESSING",
  "portrait_url": "https://example.com/portrait.jpg",
  "error_message": null,
  "result_gallery_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:15:00Z"
}
```

## 7. 错误处理

当 API 请求失败时，将返回以下格式的错误信息：

```json
{
  "detail": "错误描述信息"
}
```

常见错误包括：

- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 认证失败
- `403 Forbidden`: 无权限访问
- `404 Not Found`: 请求的资源不存在
- `422 Unprocessable Entity`: 请求数据验证失败
- `500 Internal Server Error`: 服务器内部错误

## 8. 限流

API 实施请求限流以保护服务器资源。默认限制为每分钟100个请求，超过限制将返回 `429 Too Many Requests` 状态码。

## 9. 健康检查

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

---
**API 版本**: 1.0  
**最后更新**: 2025-01-04