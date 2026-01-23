# AI Test Assistant Service - 测试指南

## 快速开始

### 1. 环境准备

确保已安装 Python 3.11+ 和所需依赖：

```bash
cd ai-service
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（或复制 `.env.example`）：

```bash
# BRConnector API 配置（必需）
BRCONNECTOR_API_KEY=your_api_key_here
BRCONNECTOR_BASE_URL=https://api.brconnector.com

# Go 后端配置（必需）
GO_BACKEND_URL=http://localhost:8080

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

**重要**：
- `BRCONNECTOR_API_KEY` 是必需的，用于调用 Claude API
- `GO_BACKEND_URL` 是必需的，用于检索 PRD 和测试用例

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 运行测试脚本

```bash
python test_api.py
```

## API 端点说明

### 1. 健康检查

```bash
GET /health
```

**响应示例**：
```json
{
  "status": "healthy",
  "service": "ai-test-assistant",
  "version": "1.0.0"
}
```

### 2. 生成测试用例

```bash
POST /ai/generate
```

**请求示例**：
```json
{
  "message": "用户登录功能：支持用户名密码登录，需要验证码",
  "project_id": 1,
  "conversation_id": "conv-123",
  "context": {}
}
```

**响应示例**：
```json
{
  "success": true,
  "task_type": "GENERATE_TEST_CASES",
  "conversation_id": "conv-123",
  "test_cases": [
    {
      "title": "验证用户名密码登录成功",
      "preconditions": "用户已注册",
      "steps": [
        {
          "step_number": 1,
          "action": "输入用户名",
          "expected": "用户名输入框显示输入内容"
        },
        {
          "step_number": 2,
          "action": "输入密码",
          "expected": "密码输入框显示掩码"
        },
        {
          "step_number": 3,
          "action": "输入验证码",
          "expected": "验证码输入框显示输入内容"
        },
        {
          "step_number": 4,
          "action": "点击登录按钮",
          "expected": "跳转到首页"
        }
      ],
      "expected_result": "用户成功登录系统",
      "priority": "P0",
      "type": "functional"
    }
  ],
  "metadata": {
    "coverage_score": 85,
    "total_generated": 5,
    "approved_count": 5
  }
}
```

### 3. 流式对话（SSE）

```bash
POST /ai/chat/stream
```

**请求示例**：
```json
{
  "message": "帮我分析一下用户登录功能的测试点",
  "project_id": 1,
  "conversation_id": "conv-123",
  "stream": true
}
```

**响应格式**（Server-Sent Events）：
```
data: {"type": "start", "conversation_id": "conv-123"}

data: {"type": "content", "content": "用户登录功能"}

data: {"type": "content", "content": "的测试点包括："}

data: {"type": "content", "content": "\n1. 正常登录流程"}

data: {"type": "done", "conversation_id": "conv-123"}
```

### 4. 列出对话

```bash
GET /ai/conversations?project_id=1
```

**响应示例**：
```json
{
  "success": true,
  "conversations": [
    {
      "conversation_id": "conv-123",
      "project_id": "1",
      "message_count": 4,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:10:00"
    }
  ],
  "total": 1
}
```

### 5. 删除对话

```bash
DELETE /ai/conversations/{conversation_id}
```

**响应示例**：
```json
{
  "success": true,
  "message": "对话 conv-123 已删除"
}
```

## 使用 curl 测试

### 测试健康检查

```bash
curl http://localhost:8000/health
```

### 测试生成测试用例

```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "用户登录功能：支持用户名密码登录",
    "project_id": 1
  }'
```

### 测试流式对话

```bash
curl -X POST http://localhost:8000/ai/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我分析一下用户登录功能的测试点",
    "project_id": 1,
    "stream": true
  }'
```

## 使用 Postman 测试

1. 导入 API 端点到 Postman
2. 设置环境变量：
   - `base_url`: http://localhost:8000
3. 测试各个端点

## 常见问题

### 1. 服务启动失败

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决**：
```bash
pip install -r requirements.txt
```

### 2. API 调用失败

**问题**：`401 Unauthorized` 或 `API key invalid`

**解决**：
- 检查 `.env` 文件中的 `BRCONNECTOR_API_KEY` 是否正确
- 确保 API key 有效且未过期

### 3. 检索失败

**问题**：`Connection refused` 或 `Go backend not available`

**解决**：
- 确保 Go 后端服务已启动（`http://localhost:8080`）
- 检查 `.env` 文件中的 `GO_BACKEND_URL` 是否正确

### 4. 响应超时

**问题**：请求超时或响应时间过长

**解决**：
- 增加请求超时时间（默认 120 秒）
- 检查 BRConnector API 是否正常
- 检查网络连接

## 下一步

完成 API 测试后，你可以：

1. **集成 Go 后端**：实现任务 10-14，打通整个后端系统
2. **开发前端**：实现任务 15-21，创建用户界面
3. **端到端测试**：实现任务 22，进行完整的系统测试

## 测试检查清单

- [ ] 健康检查端点正常
- [ ] 生成测试用例端点正常（简单需求）
- [ ] 生成测试用例端点正常（复杂需求）
- [ ] 流式对话端点正常
- [ ] 列出对话端点正常
- [ ] 删除对话端点正常
- [ ] API 文档可访问（/docs）
- [ ] 错误处理正常
- [ ] 日志输出正常

## 性能基准

- 简单需求生成测试用例：< 30 秒
- 复杂需求生成测试用例：< 60 秒
- 流式对话首字响应：< 2 秒
- 健康检查：< 100ms

## 支持

如有问题，请查看：
- 日志输出（控制台）
- API 文档（/docs）
- 设计文档（.kiro/specs/ai-test-assistant/design.md）
