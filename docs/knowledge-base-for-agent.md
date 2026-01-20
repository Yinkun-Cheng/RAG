# AI Agent 调用知识库 - 核心设计文档

## 项目核心定位

本系统的核心是**作为外部知识库供 AI Agent（如 Dify）调用**，为 Agent 提供结构化、精准的测试知识检索能力。

## 通用知识库的问题

### 1. 数据结构问题
- **通用知识库**：以文档为单位存储，缺乏结构化字段
- **对测试行业的影响**：无法区分 PRD、测试用例、测试步骤等不同类型的测试数据
- **本系统解决方案**：按测试领域设计专门的数据结构（PRD、TestCase、TestStep），每种类型都有专属字段（优先级、类型、状态、前置条件、预期结果等）

### 2. 检索精度问题
- **通用知识库**：仅支持语义相似度检索
- **对测试行业的影响**：无法按模块、版本、优先级等维度精确筛选
- **本系统解决方案**：结合向量检索和结构化过滤，支持多维度组合查询（project_id + app_version + module + priority + type）

### 3. 关联关系问题
- **通用知识库**：文档之间是独立的，没有关联关系
- **对测试行业的影响**：无法追踪"某个 PRD 对应哪些测试用例"、"修改 PRD 会影响哪些测试用例"
- **本系统解决方案**：建立 PRD 与测试用例的关联关系，支持影响分析和关联推荐

### 4. 版本管理问题
- **通用知识库**：不支持版本管理，只能覆盖更新
- **对测试行业的影响**：无法查询"v1.0 版本的登录功能需求是什么"
- **本系统解决方案**：PRD 和测试用例都支持版本管理，可以按 app_version 查询历史版本

### 5. 元数据丢失问题
- **通用知识库**：向量化时丢失大量元数据
- **对测试行业的影响**：Agent 无法获取测试用例的优先级、类型、状态等关键信息
- **本系统解决方案**：向量化时保留完整元数据（project_id, project_name, prd_id, module, app_version, priority, type, status, tags）

## 为 AI Agent 设计的核心 API

### 1. Dify 外部知识库 API

**接口地址**：`POST /api/v1/dify/retrieval`

**功能**：供 Dify Agent 调用，检索测试知识

**请求参数**：
```json
{
  "query": "用户登录功能的测试用例",
  "top_k": 5,
  "score_threshold": 0.7,
  "filters": {
    "project_id": "proj-1",
    "app_version": "v1.0.0",
    "module": "用户管理/用户登录",
    "type": "functional",
    "priority": "high"
  }
}
```

**返回数据**：
```json
{
  "records": [
    {
      "content": "测试用例：用户登录-密码错误\n前置条件：用户已注册\n测试步骤：\n1. 打开登录页面\n2. 输入用户名：test@example.com\n3. 输入错误密码：wrong123\n4. 点击登录按钮\n预期结果：提示密码错误",
      "score": 0.95,
      "metadata": {
        "id": "tc-2",
        "type": "testcase",
        "project_id": "proj-1",
        "project_name": "电商平台",
        "app_version": "v1.0.0",
        "module": "用户管理/用户登录",
        "priority": "high",
        "test_type": "functional",
        "status": "active",
        "tags": ["核心功能"],
        "prd_id": "prd-2",
        "created_at": "2025-01-11"
      }
    }
  ]
}
```

### 2. 影响分析 API

**接口地址**：`POST /api/v1/impact-analysis`

**功能**：分析 PRD 变更会影响哪些测试用例

**请求参数**：
```json
{
  "prd_id": "prd-2",
  "change_description": "登录功能新增短信验证码登录方式"
}
```

**返回数据**：
```json
{
  "affected_testcases": [
    {
      "id": "tc-2",
      "title": "用户登录-密码错误",
      "impact_level": "high",
      "reason": "登录流程变更，需要新增短信登录测试用例"
    }
  ]
}
```

### 3. 关联推荐 API

**接口地址**：`GET /api/v1/recommend/:prd_id`

**功能**：根据 PRD 推荐相关的测试用例

**返回数据**：
```json
{
  "recommendations": [
    {
      "id": "tc-2",
      "title": "用户登录-密码错误",
      "similarity": 0.92,
      "reason": "与该 PRD 直接关联"
    }
  ]
}
```

### 4. 结构化检索 API

**接口地址**：`POST /api/v1/search`

**功能**：支持复杂的结构化查询

**请求参数**：
```json
{
  "query": "登录功能",
  "type": "testcase",
  "filters": {
    "project_id": "proj-1",
    "app_version": "v1.0.0",
    "module": "用户管理",
    "priority": ["high", "medium"],
    "status": "active"
  },
  "top_k": 10
}
```

## Agent 调用场景示例

### 场景 1：查询某版本的功能需求

**用户问题**："用户登录注册 1.0 版本都做了什么"

**Agent 处理流程**：
1. 解析用户意图：查询 v1.0 版本的用户登录注册相关 PRD
2. 调用 Dify 外部知识库 API：
   ```json
   {
     "query": "用户登录注册功能需求",
     "filters": {
       "project_id": "proj-1",
       "app_version": "v1.0.0",
       "module": "用户管理"
     }
   }
   ```
3. 获取返回结果（PRD 文档列表）
4. 整理并返回给用户

**数据完整性说明**：
- 如果 PRD 文档较长（超过 2000 字），会被分段存储
- 每个分段都包含完整的元数据（project_id, app_version, module 等）
- Agent 可以通过多次检索获取完整内容，或使用详情 API 获取完整文档

### 场景 2：查询测试用例

**用户问题**："登录功能有哪些高优先级测试用例"

**Agent 处理流程**：
1. 调用 Dify 外部知识库 API：
   ```json
   {
     "query": "登录功能测试用例",
     "filters": {
       "type": "testcase",
       "module": "用户管理/用户登录",
       "priority": "high"
     }
   }
   ```
2. 返回测试用例列表（包含测试步骤、前置条件、预期结果）

### 场景 3：影响分析

**用户问题**："如果修改登录功能的 PRD，会影响哪些测试用例"

**Agent 处理流程**：
1. 先查询登录功能的 PRD ID
2. 调用影响分析 API
3. 返回受影响的测试用例列表

## 数据完整性解决方案

针对"用户登录注册 1.0 版本都做了什么"这类查询，系统提供三种方案：

### 方案 1：摘要 + 详情链接（推荐）
- 向量化时存储 PRD 摘要（前 500 字）
- 返回结果中包含详情链接
- Agent 可以引导用户点击链接查看完整内容

### 方案 2：分段存储
- 长文档分成多个段落（每段 500 字，重叠 50 字）
- 每个段落都包含完整元数据
- Agent 可以通过多次检索获取完整内容

### 方案 3：版本查询 API
- 提供专门的 API：`GET /api/v1/prds?app_version=v1.0.0&module=用户管理`
- 返回完整的 PRD 列表（不经过向量检索）
- 适合"查询某版本所有功能"的场景

### 推荐组合方案
- 向量化存储：摘要（500 字）+ 完整元数据
- 提供详情 API：`GET /api/v1/prds/:id`（返回完整内容）
- 提供版本查询 API：`GET /api/v1/prds?filters=...`（结构化查询）

Agent 根据用户问题选择合适的 API：
- 语义搜索 → Dify 外部知识库 API（返回摘要）
- 查看详情 → 详情 API（返回完整内容）
- 批量查询 → 版本查询 API（返回列表）

## 向量化设计

### 存储的元数据
```json
{
  "project_id": "proj-1",
  "project_name": "电商平台",
  "type": "prd | testcase",
  "prd_id": "prd-2",
  "module": "用户管理/用户登录",
  "app_version": "v1.0.0",
  "priority": "high",
  "test_type": "functional",
  "status": "active | draft | archived",
  "tags": ["核心功能", "高优先级"],
  "created_at": "2025-01-11",
  "updated_at": "2025-01-15"
}
```

### Dify 调用时的过滤
Dify 在调用外部知识库时，会自动传递 `metadata_condition`：
```json
{
  "metadata_condition": {
    "project_id": "proj-1"
  }
}
```

这样可以实现多项目隔离，每个 Dify Agent 只能访问自己项目的数据。

## 总结

本系统与通用知识库的核心区别：
1. **专为测试领域设计**：数据结构、字段、关联关系都针对测试场景优化
2. **结构化 + 语义化**：既支持精确筛选，又支持模糊搜索
3. **完整的元数据**：Agent 可以获取测试用例的所有关键信息
4. **版本管理**：支持查询历史版本的需求和测试用例
5. **关联分析**：支持影响分析和关联推荐

这些特性使得 AI Agent 能够更准确、更高效地回答测试相关的问题。
