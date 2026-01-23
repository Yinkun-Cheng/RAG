# 快速开始 - AI Test Assistant Service

## 🚀 5 分钟快速测试

### 步骤 1: 安装依赖

```bash
cd ai-service
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

编辑 `.env` 文件，**至少配置以下两项**：

```bash
# 必需：BRConnector API 密钥（用于调用 Claude）
BRCONNECTOR_API_KEY=your-actual-api-key-here

# 必需：Go 后端 URL（用于检索 PRD 和测试用例）
GO_BACKEND_URL=http://localhost:8080
```

### 步骤 3: 启动服务

```bash
python main.py
```

你应该看到：

```
🚀 Starting AI Test Assistant Service...
Environment: development
Service URL: http://0.0.0.0:5000
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

### 步骤 4: 测试服务

**方法 1：使用测试脚本（推荐）**

```bash
python test_api.py
```

**方法 2：使用 curl**

```bash
# 测试健康检查
curl http://localhost:5000/health

# 测试生成测试用例
curl -X POST http://localhost:5000/ai/generate \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"用户登录功能\", \"project_id\": 1}"
```

**方法 3：使用浏览器**

访问 API 文档：http://localhost:5000/docs

## 📝 测试示例

### 示例 1: 简单需求

**请求**：
```json
{
  "message": "用户登录功能：支持用户名密码登录",
  "project_id": 1
}
```

**预期结果**：
- 生成 3-5 个测试用例
- 包含主流程、异常流程、边界值测试
- 每个测试用例包含标题、前置条件、步骤、预期结果

### 示例 2: 复杂需求

**请求**：
```json
{
  "message": "用户注册功能：支持手机号注册，需要验证码，密码长度 8-20 位，必须包含字母和数字",
  "project_id": 1
}
```

**预期结果**：
- 生成 5-10 个测试用例
- 覆盖所有功能点和约束条件
- 包含边界值测试（密码长度 7、8、20、21 位）

### 示例 3: 流式对话

**请求**：
```json
{
  "message": "帮我分析一下用户登录功能的测试点",
  "project_id": 1,
  "stream": true
}
```

**预期结果**：
- 实时流式返回 AI 分析结果
- 可以看到打字机效果

## ⚠️ 常见问题

### 问题 1: 服务启动失败

**错误**：`ModuleNotFoundError`

**解决**：
```bash
pip install -r requirements.txt
```

### 问题 2: API 调用失败

**错误**：`401 Unauthorized`

**原因**：BRConnector API 密钥无效

**解决**：
1. 检查 `.env` 文件中的 `BRCONNECTOR_API_KEY`
2. 确保 API key 有效且未过期

### 问题 3: 检索失败

**错误**：`Connection refused` 或 `Go backend not available`

**原因**：Go 后端服务未启动

**解决**：
1. 启动 Go 后端服务：`cd backend && go run cmd/server/main.go`
2. 或者暂时跳过检索测试（其他功能仍可用）

### 问题 4: 响应慢

**原因**：首次调用需要初始化 Agent 和 Workflows

**正常情况**：
- 首次请求：30-60 秒
- 后续请求：10-30 秒

## 📊 测试检查清单

完成以下测试，确保服务正常：

- [ ] ✅ 服务启动成功
- [ ] ✅ 健康检查端点正常（/health）
- [ ] ✅ API 文档可访问（/docs）
- [ ] ✅ 生成测试用例成功（简单需求）
- [ ] ✅ 生成测试用例成功（复杂需求）
- [ ] ✅ 流式对话成功
- [ ] ✅ 列出对话成功
- [ ] ✅ 删除对话成功

## 🎯 下一步

测试成功后，你可以：

1. **查看详细文档**：`TESTING.md`
2. **继续开发**：实现任务 8.3-8.4（错误处理和集成测试）
3. **集成 Go 后端**：实现任务 10-14
4. **开发前端**：实现任务 15-21

## 💡 提示

- 使用 `python test_api.py` 进行自动化测试
- 使用 `/docs` 查看完整的 API 文档
- 查看控制台日志了解详细执行过程
- 第一次请求会比较慢（需要初始化）

## 📞 需要帮助？

- 查看日志输出（控制台）
- 查看 `TESTING.md` 获取详细测试指南
- 查看 `.kiro/specs/ai-test-assistant/design.md` 了解系统设计

---

**祝测试顺利！** 🎉
