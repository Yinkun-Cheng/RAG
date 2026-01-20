# 系统配置 - LLM 大模型配置

## 📋 新增配置项

在系统配置页面（`frontend/src/pages/Settings/index.tsx`）新增了 **LLM 大模型** 配置 Tab。

## 🎯 配置项说明

### **1. 基础配置**

| 配置项 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| **模型提供商** | 选择 LLM 提供商 | Claude | ✅ |
| **模型名称** | 具体的模型名称 | claude-3-5-sonnet-20241022 | ✅ |
| **API Key** | 模型 API 密钥 | - | ✅ |
| **API Base URL** | API 基础地址（可选） | - | ❌ |
| **Temperature** | 输出随机性控制（0-1） | 0.3 | ✅ |
| **Max Tokens** | 最大令牌数 | 4000 | ✅ |

### **2. 支持的模型提供商**

#### **OpenAI**
```
模型名称示例：
- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo

API Base URL：https://api.openai.com/v1
```

#### **Claude (Anthropic)** ⭐ 推荐
```
模型名称示例：
- claude-3-5-sonnet-20241022 （推荐）
- claude-3-opus-20240229
- claude-3-sonnet-20240229

API Base URL：https://api.anthropic.com
```

#### **Azure OpenAI**
```
模型名称：部署名称
API Base URL：https://{your-resource-name}.openai.azure.com
```

#### **本地模型 (Ollama)**
```
模型名称示例：
- llama3
- mistral
- qwen

API Base URL：http://localhost:11434
```

#### **自定义 API**
```
支持任何兼容 OpenAI API 格式的服务
```

### **3. 使用场景配置**

| 功能 | 说明 | 默认状态 |
|------|------|----------|
| **启用影响分析** | 使用 LLM 分析 PRD 变更对测试用例的影响 | ✅ 开启 |
| **启用智能推荐** | 使用 LLM 推荐相关的 PRD 和测试用例 | ✅ 开启 |
| **启用测试用例生成建议** | 使用 LLM 根据 PRD 生成测试用例建议 | ✅ 开启 |

### **4. 成本控制配置**

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| **启用结果缓存** | 缓存 LLM 分析结果，减少重复调用 | ✅ 开启 |
| **缓存过期时间** | 缓存结果的有效期（小时） | 24 小时 |
| **调用频率限制** | 限制 LLM 调用频率（次/分钟） | 10 次/分钟 |

## 🎨 UI 设计

### **Tab 顺序**
```
系统配置
├─ LLM 大模型      ← 新增（第一个 Tab）
├─ 向量数据库
├─ 向量化模型
├─ Dify 集成
└─ 高级配置
```

### **配置区域**
```
┌────────────────────────────────────────┐
│ LLM 大模型配置                          │
├────────────────────────────────────────┤
│                                         │
│ 📊 基础配置                             │
│ - 模型提供商                            │
│ - 模型名称                              │
│ - API Key                               │
│ - API Base URL                          │
│ - Temperature                           │
│ - Max Tokens                            │
│ [测试 LLM 连接]                         │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                         │
│ 🎯 使用场景配置                         │
│ - 启用影响分析                          │
│ - 启用智能推荐                          │
│ - 启用测试用例生成建议                  │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                         │
│ 💰 成本控制                             │
│ - 启用结果缓存                          │
│ - 缓存过期时间                          │
│ - 调用频率限制                          │
│                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                         │
│ ✅ 模型推荐                             │
│ Claude 3.5 Sonnet（推荐）               │
│ GPT-4 Turbo                             │
│ 本地模型（Ollama）                      │
└────────────────────────────────────────┘
```

## 🔧 后端 API 接口

### **保存配置**
```typescript
POST /api/v1/settings/llm
{
  "provider": "claude",
  "model": "claude-3-5-sonnet-20241022",
  "api_key": "sk-xxx",
  "api_base": "https://api.anthropic.com",
  "temperature": 0.3,
  "max_tokens": 4000,
  "enable_impact_analysis": true,
  "enable_recommendation": true,
  "enable_test_generation": true,
  "cache_enabled": true,
  "cache_ttl": 24,
  "rate_limit": 10
}
```

### **测试 LLM 连接**
```typescript
POST /api/v1/settings/test-llm
{
  "provider": "claude",
  "model": "claude-3-5-sonnet-20241022",
  "api_key": "sk-xxx",
  "api_base": "https://api.anthropic.com"
}

// 返回
{
  "success": true,
  "message": "LLM 连接成功",
  "model_info": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 200000,
    "supports_json": true
  }
}
```

### **获取配置**
```typescript
GET /api/v1/settings/llm

// 返回
{
  "provider": "claude",
  "model": "claude-3-5-sonnet-20241022",
  "api_base": "https://api.anthropic.com",
  "temperature": 0.3,
  "max_tokens": 4000,
  // API Key 不返回，只返回是否已配置
  "api_key_configured": true,
  "enable_impact_analysis": true,
  "enable_recommendation": true,
  "enable_test_generation": true,
  "cache_enabled": true,
  "cache_ttl": 24,
  "rate_limit": 10
}
```

## 💡 使用建议

### **1. Temperature 设置**
- **影响分析**：建议 0.3（低温度，保证输出稳定）
- **智能推荐**：建议 0.5（中等温度，平衡创造性和稳定性）
- **测试用例生成**：建议 0.7（高温度，增加创造性）

### **2. Max Tokens 设置**
- **影响分析**：建议 4000+（需要详细分析）
- **智能推荐**：建议 2000（简短推荐）
- **测试用例生成**：建议 3000（详细测试场景）

### **3. 成本优化**
- ✅ 启用结果缓存（减少重复调用）
- ✅ 设置合理的缓存过期时间（24 小时）
- ✅ 设置调用频率限制（避免超出 API 限额）
- ✅ 使用向量检索先过滤，只把相关内容给 LLM

### **4. 模型选择**
- **生产环境**：Claude 3.5 Sonnet（推荐）或 GPT-4 Turbo
- **开发环境**：GPT-3.5 Turbo（成本低）
- **隐私要求**：本地模型（Ollama + Llama 3）

## 🔒 安全性

### **API Key 存储**
- 后端加密存储 API Key
- 前端不显示完整 API Key
- 只显示是否已配置

### **权限控制**
- 只有管理员可以修改 LLM 配置
- 普通用户只能查看是否启用

## 📊 监控指标

建议在 Dashboard 中显示：
- LLM 调用次数（今日/本周/本月）
- LLM 调用成功率
- 平均响应时间
- 缓存命中率
- 预估成本

## 🎯 与其他功能的关联

### **影响分析页面**
- 使用 LLM 配置中的模型
- 调用 `/api/v1/impact-analysis/version-compare` 时自动使用配置的 LLM

### **智能推荐功能**（待实现）
- 在 PRD 详情页显示相关推荐
- 在测试用例详情页显示相关推荐

### **测试用例生成**（待实现）
- 根据 PRD 内容生成测试用例建议

## ✅ 完成状态

- ✅ UI 设计完成
- ✅ 配置项完整
- ✅ 表单验证
- ✅ 提示信息
- ⏳ 后端 API 待实现
- ⏳ 测试连接功能待实现

## 🚀 测试方法

1. 访问系统配置页面
2. 点击"LLM 大模型" Tab
3. 填写配置信息
4. 点击"测试 LLM 连接"按钮
5. 点击"保存配置"按钮
6. 前往影响分析页面测试功能

---

现在系统配置已经完整了，包含了所有必要的配置项：
1. ✅ LLM 大模型配置（新增）
2. ✅ 向量数据库配置
3. ✅ 向量化模型配置
4. ✅ Dify 集成配置
5. ✅ 高级配置
