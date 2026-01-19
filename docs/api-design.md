# API 接口设计文档

## 概述

本文档定义了测试用例知识库管理系统的所有 RESTful API 接口。

## 基础信息

- **Base URL**: `http://localhost:8080/api/v1`
- **认证方式**: 单人使用，暂不需要认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "error message",
  "error": "detailed error information"
}
```

### HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 1. 功能模块 API

### 1.1 获取模块树

```
GET /modules/tree
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "mod-001",
      "name": "用户模块",
      "description": "用户相关功能",
      "children": [
        {
          "id": "mod-002",
          "name": "登录注册",
          "description": "登录注册功能",
          "children": []
        }
      ]
    }
  ]
}
```

### 1.2 创建模块

```
POST /modules
```

**请求体**：
```json
{
  "name": "新模块",
  "description": "模块描述",
  "parent_id": "mod-001"
}
```

### 1.3 更新模块

```
PUT /modules/:id
```

### 1.4 删除模块

```
DELETE /modules/:id
```

## 2. PRD 文档 API

### 2.1 获取 PRD 列表

```
GET /prds
```

**查询参数**：
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）
- `module_id`: 模块 ID 过滤
- `status`: 状态过滤（draft/review/approved/published）
- `keyword`: 关键词搜索（标题、内容）
- `tags`: 标签过滤（逗号分隔）

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "prd-001",
        "code": "PRD_LOGIN_001",
        "title": "用户登录功能需求",
        "version": "v1.0",
        "module_id": "mod-002",
        "module_name": "登录注册",
        "status": "published",
        "author": "张三",
        "tags": ["登录", "认证"],
        "created_at": "2025-01-19T10:00:00Z",
        "updated_at": "2025-01-19T10:00:00Z"
      }
    ]
  }
}
```

### 2.2 获取 PRD 详情

```
GET /prds/:id
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "prd-001",
    "code": "PRD_LOGIN_001",
    "title": "用户登录功能需求",
    "version": "v1.0",
    "module_id": "mod-002",
    "module_name": "登录注册",
    "content": "# 用户登录功能\n\n## 功能描述\n...",
    "status": "published",
    "author": "张三",
    "tags": [
      {
        "id": "tag-001",
        "name": "登录",
        "color": "#f50"
      }
    ],
    "versions": [
      {
        "version": "v1.0",
        "created_at": "2025-01-19T10:00:00Z"
      }
    ],
    "related_test_cases": [
      {
        "id": "tc-001",
        "code": "TC_LOGIN_001",
        "title": "正常登录流程验证"
      }
    ],
    "created_at": "2025-01-19T10:00:00Z",
    "updated_at": "2025-01-19T10:00:00Z"
  }
}
```

### 2.3 创建 PRD

```
POST /prds
```

**请求体**：
```json
{
  "code": "PRD_LOGIN_001",
  "title": "用户登录功能需求",
  "version": "v1.0",
  "module_id": "mod-002",
  "content": "# 用户登录功能\n\n## 功能描述\n...",
  "status": "draft",
  "author": "张三",
  "tags": ["tag-001", "tag-002"]
}
```

### 2.4 更新 PRD

```
PUT /prds/:id
```

**请求体**：同创建，支持部分更新

**查询参数**：
- `create_version`: 是否创建新版本（true/false，默认 false）

### 2.5 删除 PRD

```
DELETE /prds/:id
```

### 2.6 获取 PRD 版本历史

```
GET /prds/:id/versions
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "ver-001",
      "version": "v1.0",
      "title": "用户登录功能需求",
      "change_log": "初始版本",
      "created_by": "张三",
      "created_at": "2025-01-19T10:00:00Z"
    }
  ]
}
```

### 2.7 获取特定版本内容

```
GET /prds/:id/versions/:version
```

## 3. 测试用例 API

### 3.1 获取测试用例列表

```
GET /testcases
```

**查询参数**：
- `page`: 页码
- `page_size`: 每页数量
- `prd_id`: PRD ID 过滤
- `module_id`: 模块 ID 过滤
- `priority`: 优先级过滤（P0/P1/P2/P3）
- `type`: 类型过滤
- `status`: 状态过滤
- `tags`: 标签过滤
- `keyword`: 关键词搜索

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 500,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "tc-001",
        "code": "TC_LOGIN_001",
        "title": "正常登录流程验证",
        "prd_code": "PRD_LOGIN_001",
        "prd_version": "v1.0",
        "module_name": "登录注册",
        "priority": "P0",
        "type": "functional",
        "status": "active",
        "tags": ["登录", "冒烟测试"],
        "created_at": "2025-01-19T10:00:00Z",
        "updated_at": "2025-01-19T10:00:00Z"
      }
    ]
  }
}
```

### 3.2 获取测试用例详情

```
GET /testcases/:id
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "tc-001",
    "code": "TC_LOGIN_001",
    "title": "正常登录流程验证",
    "prd_id": "prd-001",
    "prd_code": "PRD_LOGIN_001",
    "prd_version": "v1.0",
    "module_id": "mod-002",
    "module_name": "登录注册",
    "preconditions": "1. 用户已注册\n2. 账号状态正常",
    "steps": [
      {
        "step_number": 1,
        "action": "打开 APP 登录页面",
        "test_data": "",
        "expected": "显示登录页面",
        "screenshots": [
          {
            "id": "img-001",
            "file_name": "login_page.png",
            "file_path": "/uploads/screenshots/login_page.png",
            "url": "http://localhost:8080/uploads/screenshots/login_page.png"
          }
        ]
      },
      {
        "step_number": 2,
        "action": "输入正确的手机号",
        "test_data": "13800138000",
        "expected": "手机号输入框显示输入内容",
        "screenshots": []
      }
    ],
    "expected_result": "登录成功，跳转到首页",
    "priority": "P0",
    "type": "functional",
    "status": "active",
    "tags": [
      {
        "id": "tag-001",
        "name": "登录",
        "color": "#f50"
      }
    ],
    "created_at": "2025-01-19T10:00:00Z",
    "updated_at": "2025-01-19T10:00:00Z"
  }
}
```

### 3.3 创建测试用例

```
POST /testcases
```

**请求体**：
```json
{
  "code": "TC_LOGIN_001",
  "title": "正常登录流程验证",
  "prd_id": "prd-001",
  "prd_version": "v1.0",
  "module_id": "mod-002",
  "preconditions": "1. 用户已注册\n2. 账号状态正常",
  "steps": [
    {
      "step_number": 1,
      "action": "打开 APP 登录页面",
      "test_data": "",
      "expected": "显示登录页面"
    }
  ],
  "expected_result": "登录成功，跳转到首页",
  "priority": "P0",
  "type": "functional",
  "tags": ["tag-001", "tag-002"]
}
```

### 3.4 更新测试用例

```
PUT /testcases/:id
```

**查询参数**：
- `create_version`: 是否创建版本历史（true/false）

### 3.5 删除测试用例

```
DELETE /testcases/:id
```

### 3.6 批量删除测试用例

```
POST /testcases/batch-delete
```

**请求体**：
```json
{
  "ids": ["tc-001", "tc-002", "tc-003"]
}
```

## 4. 文件上传 API

### 4.1 上传截图

```
POST /upload/screenshot
```

**请求**：multipart/form-data
- `file`: 图片文件
- `test_step_id`: 测试步骤 ID（可选）

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "img-001",
    "file_name": "screenshot.png",
    "file_path": "/uploads/screenshots/2025/01/19/screenshot.png",
    "url": "http://localhost:8080/uploads/screenshots/2025/01/19/screenshot.png",
    "file_size": 102400,
    "mime_type": "image/png"
  }
}
```

### 4.2 删除文件

```
DELETE /upload/:id
```

## 5. 标签 API

### 5.1 获取所有标签

```
GET /tags
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "tag-001",
      "name": "登录",
      "color": "#f50",
      "description": "登录相关",
      "usage_count": 15
    }
  ]
}
```

### 5.2 创建标签

```
POST /tags
```

**请求体**：
```json
{
  "name": "新标签",
  "color": "#87d068",
  "description": "标签描述"
}
```

### 5.3 更新标签

```
PUT /tags/:id
```

### 5.4 删除标签

```
DELETE /tags/:id
```

## 6. 导入 API

### 6.1 导入 Excel 测试用例

```
POST /import/excel
```

**请求**：multipart/form-data
- `file`: Excel 文件
- `module_id`: 目标模块 ID
- `prd_id`: 关联 PRD ID（可选）

**Excel 格式要求**：
| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 类型 | 标签 |
|---------|---------|---------|---------|---------|--------|------|------|
| TC_001  | 测试标题 | 前置条件 | 步骤1\n步骤2 | 预期结果 | P0 | functional | 标签1,标签2 |

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "success": 95,
    "failed": 5,
    "errors": [
      {
        "row": 10,
        "error": "用例编号重复"
      }
    ]
  }
}
```

### 6.2 导入 XMind 测试用例

```
POST /import/xmind
```

**请求**：multipart/form-data
- `file`: XMind 文件
- `module_id`: 目标模块 ID
- `prd_id`: 关联 PRD ID（可选）

### 6.3 导入 Word PRD 文档

```
POST /import/word
```

**请求**：multipart/form-data
- `file`: Word 文件
- `module_id`: 目标模块 ID

## 7. RAG 检索 API

### 7.1 语义检索

```
POST /search
```

**请求体**：
```json
{
  "query": "如何测试用户登录功能",
  "type": "all",
  "filters": {
    "module_id": "mod-002",
    "priority": ["P0", "P1"],
    "tags": ["登录"]
  },
  "limit": 10
}
```

**type 可选值**：
- `all`: 搜索所有（PRD + 测试用例）
- `prd`: 仅搜索 PRD
- `testcase`: 仅搜索测试用例

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "prds": [
      {
        "id": "prd-001",
        "code": "PRD_LOGIN_001",
        "title": "用户登录功能需求",
        "snippet": "...登录功能描述...",
        "score": 0.95
      }
    ],
    "testcases": [
      {
        "id": "tc-001",
        "code": "TC_LOGIN_001",
        "title": "正常登录流程验证",
        "snippet": "...测试步骤...",
        "score": 0.92
      }
    ]
  }
}
```

### 7.2 获取关联推荐

```
GET /recommend/:prd_id
```

**查询参数**：
- `limit`: 返回数量（默认 10）

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "related_testcases": [
      {
        "id": "tc-001",
        "code": "TC_LOGIN_001",
        "title": "正常登录流程验证",
        "relevance": 0.95
      }
    ],
    "related_prds": [
      {
        "id": "prd-002",
        "code": "PRD_AUTH_001",
        "title": "用户认证功能",
        "relevance": 0.88
      }
    ]
  }
}
```

### 7.3 影响分析

```
POST /impact-analysis
```

**请求体**：
```json
{
  "prd_id": "prd-001",
  "old_version": "v1.0",
  "new_version": "v1.1",
  "change_description": "增加短信验证码登录方式"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "affected_testcases": [
      {
        "id": "tc-001",
        "code": "TC_LOGIN_001",
        "title": "正常登录流程验证",
        "impact_level": "high",
        "suggestion": "需要新增短信验证码登录的测试用例"
      }
    ],
    "new_testcase_suggestions": [
      {
        "title": "短信验证码登录流程验证",
        "priority": "P0",
        "type": "functional"
      }
    ],
    "deprecated_testcases": []
  }
}
```

## 8. Dify 外部知识库 API

### 8.1 Dify 检索接口

```
POST /dify/retrieval
```

**请求体**（符合 Dify 规范）：
```json
{
  "query": "用户登录功能的测试用例",
  "top_k": 5,
  "score_threshold": 0.7,
  "filters": {
    "type": "testcase",
    "priority": ["P0", "P1"]
  }
}
```

**响应示例**（符合 Dify 规范）：
```json
{
  "records": [
    {
      "content": "用例编号：TC_LOGIN_001\n用例标题：正常登录流程验证\n...",
      "score": 0.95,
      "metadata": {
        "id": "tc-001",
        "type": "testcase",
        "code": "TC_LOGIN_001",
        "priority": "P0",
        "url": "http://localhost:5173/testcases/tc-001"
      }
    }
  ]
}
```

## 9. 统计 API

### 9.1 获取统计数据

```
GET /statistics
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_prds": 50,
    "total_testcases": 500,
    "testcases_by_priority": {
      "P0": 100,
      "P1": 200,
      "P2": 150,
      "P3": 50
    },
    "testcases_by_type": {
      "functional": 300,
      "performance": 100,
      "compatibility": 50,
      "security": 50
    },
    "testcases_by_module": [
      {
        "module_name": "登录注册",
        "count": 50
      }
    ]
  }
}
```

## 10. 健康检查 API

### 10.1 健康检查

```
GET /health
```

**响应示例**：
```json
{
  "status": "healthy",
  "timestamp": "2025-01-19T10:00:00Z",
  "services": {
    "postgres": "connected",
    "weaviate": "connected"
  }
}
```

## 错误码说明

| 错误码 | 说明 |
|-------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如编号重复） |
| 500 | 服务器内部错误 |
| 1001 | 数据库错误 |
| 1002 | 向量数据库错误 |
| 1003 | 文件上传错误 |
| 1004 | 文件解析错误 |

## 接口调用示例

### 使用 curl

```bash
# 创建 PRD
curl -X POST http://localhost:8080/api/v1/prds \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PRD_LOGIN_001",
    "title": "用户登录功能需求",
    "version": "v1.0",
    "module_id": "mod-002",
    "content": "# 用户登录功能",
    "status": "draft"
  }'

# 语义检索
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何测试用户登录",
    "type": "testcase",
    "limit": 5
  }'
```

### 使用 JavaScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080/api/v1'
});

// 创建测试用例
const createTestCase = async (data) => {
  const response = await api.post('/testcases', data);
  return response.data;
};

// 语义检索
const search = async (query) => {
  const response = await api.post('/search', {
    query,
    type: 'all',
    limit: 10
  });
  return response.data;
};
```
