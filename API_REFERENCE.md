# Superstar AI - API接口详细说明文档

## 1. API基础信息

### 1.1 API版本
- **版本**: v1
- **基础路径**: `/api/v1`
- **协议**: HTTPS (生产环境) / HTTP (开发环境)
- **内容类型**: `application/json`

### 1.2 认证方式
- **类型**: JWT Bearer Token
- **头部**: `Authorization: Bearer <token>`
- **获取方式**: 通过 `/auth/login/access-token` 接口获取

### 1.3 响应格式
- **成功响应**: `200 OK` 或 `201 Created`
- **错误响应**: 标准HTTP错误码 + JSON错误信息

### 1.4 通用错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

## 2. 认证API

### 2.1 用户登录
```
POST /auth/login/access-token
Content-Type: application/x-www-form-urlencoded
```

**请求参数**:
- `username` (string, required): 用户邮箱
- `password` (string, required): 用户密码

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/access-token \
  -d "username=user@example.com&password=password123"
```

**错误响应**:
- `400 Bad Request`: 用户名或密码错误
- `422 Unprocessable Entity`: 参数验证失败

### 2.2 用户注册
```
POST /users/
```

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "username"
}
```

**响应**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "username": "username",
  "balance": 0.0,
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "password": "password123", "username": "newuser"}'
```

**错误响应**:
- `400 Bad Request`: 邮箱已被注册

## 3. 用户API

### 3.1 获取当前用户信息
```
GET /users/me
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "username": "username",
  "balance": 50.0,
  "face_image_url": "http://localhost:8000/static/uploads/user_face.jpg",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

**示例请求**:
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3.2 更新用户头像
```
POST /users/face
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求参数**:
- `file` (file, required): 图像文件
- `gender` (string, optional): 性别 ("male"|"female"|"unisex", default: "female")

**响应**:
```json
{
  "url": "http://localhost:8000/static/uploads/user_face.jpg"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/users/face \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@path/to/image.jpg" \
  -F "gender=female"
```

### 3.3 用户充值
```
POST /users/topup
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "amount": 100
}
```

**响应**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "balance": 150.0,
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/users/topup \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'
```

## 4. 模板API

### 4.1 获取模板列表
```
GET /templates/
```

**查询参数**:
- `category` (string, optional): 按类别过滤模板

**响应**:
```json
[
  {
    "id": "uuid-string",
    "title": "复古胶片风格",
    "category": "复古",
    "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
    "price": 9.9,
    "usage_count": 125,
    "created_at": "2023-01-01T00:00:00"
  }
]
```

**示例请求**:
```bash
curl -X GET "http://localhost:8000/api/v1/templates/?category=复古"
```

### 4.2 获取随机模板
```
GET /templates/random
```

**响应**:
```json
{
  "id": "uuid-string",
  "title": "复古胶片风格",
  "category": "复古",
  "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
  "price": 9.9,
  "usage_count": 125,
  "created_at": "2023-01-01T00:00:00"
}
```

**示例请求**:
```bash
curl -X GET http://localhost:8000/api/v1/templates/random
```

## 5. 订单API

### 5.1 创建订单
```
POST /orders/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "template_id": "template-uuid"
}
```

**响应**:
```json
{
  "id": "order-uuid",
  "user_id": "user-uuid",
  "template_id": "template-uuid",
  "status": "PENDING",
  "amount": 9.9,
  "result_image_url": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"template_id": "template-uuid"}'
```

**错误响应**:
- `400 Bad Request`: 余额不足
- `404 Not Found`: 模板不存在

### 5.2 获取订单详情
```
GET /orders/{order_id}
Authorization: Bearer <token>
```

**路径参数**:
- `order_id` (string, required): 订单UUID

**响应**:
```json
{
  "id": "order-uuid",
  "user_id": "user-uuid",
  "template_id": "template-uuid",
  "status": "COMPLETED",
  "amount": 9.9,
  "result_image_url": "http://localhost:8000/static/uploads/result_image.jpg",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:30"
}
```

**示例请求**:
```bash
curl -X GET http://localhost:8000/api/v1/orders/order-uuid \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5.3 获取用户订单列表
```
GET /orders/
Authorization: Bearer <token>
```

**响应**:
```json
[
  {
    "id": "order-uuid",
    "user_id": "user-uuid",
    "template_id": "template-uuid",
    "status": "COMPLETED",
    "amount": 9.9,
    "result_image_url": "http://localhost:8000/static/uploads/result_image.jpg",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:30"
  }
]
```

**示例请求**:
```bash
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 6. 管理员API

### 6.1 模板管理

#### 6.1.1 创建模板
```
POST /admin/templates/
Authorization: Bearer <token>
```

**请求体**:
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

**响应**:
```json
{
  "id": "template-uuid",
  "title": "新模板标题",
  "category": "风格类别",
  "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
  "price": 19.9,
  "usage_count": 0,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/templates/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新模板标题",
    "category": "风格类别",
    "cover_image_url": "http://localhost:8000/static/uploads/template_cover.jpg",
    "price": 19.9,
    "prompt_config": {
      "base_prompt": "base prompt text",
      "variable_prompt": "variable prompt text",
      "negative_prompt": "negative prompt text"
    }
  }'
```

#### 6.1.2 删除模板
```
DELETE /admin/templates/{id}
Authorization: Bearer <token>
```

**路径参数**:
- `id` (string, required): 模板UUID

**响应**:
```json
{
  "status": "success",
  "message": "Template deleted"
}
```

**示例请求**:
```bash
curl -X DELETE http://localhost:8000/api/v1/admin/templates/template-uuid \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.2 用户管理

#### 6.2.1 获取用户列表
```
GET /admin/users
Authorization: Bearer <token>
```

**查询参数**:
- `skip` (integer, optional): 跳过的记录数，默认0
- `limit` (integer, optional): 返回的最大记录数，默认50

**响应**:
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
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    }
  ]
}
```

**示例请求**:
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users?skip=0&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.3 数据看板

#### 6.3.1 获取运营数据
```
GET /admin/stats/dashboard
Authorization: Bearer <token>
```

**响应**:
```json
{
  "total_users": 125,
  "total_revenue": 2500.0,
  "total_orders": 350,
  "total_templates": 25
}
```

**示例请求**:
```bash
curl -X GET http://localhost:8000/api/v1/admin/stats/dashboard \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 7. 工具API

### 7.1 文件上传
```
POST /utils/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求参数**:
- `file` (file, required): 要上传的文件

**响应**:
```json
{
  "url": "http://localhost:8000/static/uploads/filename.jpg"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/api/v1/utils/upload \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@path/to/image.jpg"
```

## 8. 健康检查API

### 8.1 健康检查
```
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

**示例请求**:
```bash
curl -X GET http://localhost:8000/health
```

## 9. 错误码说明

### 9.1 HTTP状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或认证失败 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 请求数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 9.2 业务错误码

| 错误码 | 含义 | 说明 |
|--------|------|------|
| INSUFFICIENT_BALANCE | 余额不足 | 用户余额不足以完成交易 |
| TEMPLATE_NOT_FOUND | 模板不存在 | 请求的模板不存在 |
| ORDER_NOT_FOUND | 订单不存在 | 请求的订单不存在 |
| USER_NOT_FOUND | 用户不存在 | 请求的用户不存在 |
| INVALID_CREDENTIALS | 凭据无效 | 用户名或密码错误 |
| EMAIL_ALREADY_REGISTERED | 邮箱已注册 | 邮箱已被其他用户注册 |
| PERMISSION_DENIED | 权限不足 | 当前用户无足够权限执行操作 |

## 10. API最佳实践

### 10.1 请求最佳实践

1. **认证令牌管理**:
   - 在请求头中始终包含有效的JWT令牌
   - 令牌过期时重新获取新令牌
   - 安全存储令牌，避免泄露

2. **错误处理**:
   - 检查HTTP状态码
   - 解析错误响应以获取详细信息
   - 实现重试逻辑（对于临时错误）

3. **数据验证**:
   - 客户端验证后再发送请求
   - 服务端也会进行验证

### 10.2 性能优化

1. **批量操作**:
   - 尽可能使用批量API减少请求次数
   - 合理使用分页参数

2. **缓存策略**:
   - 对于不经常变化的数据，考虑客户端缓存
   - 使用ETag或Last-Modified进行条件请求

### 10.3 安全注意事项

1. **敏感信息保护**:
   - 不要在URL中传递敏感信息
   - 使用HTTPS加密传输
   - 定期更换API密钥

2. **速率限制**:
   - 遵守API速率限制
   - 实现指数退避重试机制

---

此API参考文档详细说明了Superstar AI项目的全部API接口，包括请求格式、响应格式、错误处理等信息。