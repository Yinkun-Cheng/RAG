# 数据库设计文档

## 概述

本系统使用 PostgreSQL 作为主数据库存储结构化数据，使用 Weaviate 作为向量数据库存储文档向量用于语义检索。

## PostgreSQL 数据库设计

### 1. 功能模块表（modules）

存储产品功能模块信息，用于组织 PRD 和测试用例。

```sql
CREATE TABLE modules (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id VARCHAR(36) REFERENCES modules(id) ON DELETE CASCADE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_modules_parent_id ON modules(parent_id);
CREATE INDEX idx_modules_deleted_at ON modules(deleted_at);
```

**字段说明**：
- `id`: 主键，UUID
- `name`: 模块名称（如：用户模块、支付模块）
- `description`: 模块描述
- `parent_id`: 父模块 ID，支持树形结构
- `sort_order`: 排序字段
- `deleted_at`: 软删除标记

### 2. PRD 文档表（prd_documents）

存储产品需求文档的主要信息。

```sql
CREATE TABLE prd_documents (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    version VARCHAR(20) NOT NULL,
    module_id VARCHAR(36) REFERENCES modules(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    author VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_prd_documents_module_id ON prd_documents(module_id);
CREATE INDEX idx_prd_documents_status ON prd_documents(status);
CREATE INDEX idx_prd_documents_version ON prd_documents(version);
CREATE INDEX idx_prd_documents_deleted_at ON prd_documents(deleted_at);
CREATE INDEX idx_prd_documents_code ON prd_documents(code);
```

**字段说明**：
- `id`: 主键，UUID
- `code`: PRD 编号（如：PRD_LOGIN_001）
- `title`: PRD 标题
- `version`: 版本号（如：v1.0, v1.1）
- `module_id`: 关联的功能模块
- `content`: Markdown 格式的文档内容
- `status`: 状态（draft/review/approved/published/deprecated）
- `author`: 作者

### 3. PRD 版本历史表（prd_versions）

记录 PRD 文档的所有历史版本。

```sql
CREATE TABLE prd_versions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    prd_id VARCHAR(36) NOT NULL REFERENCES prd_documents(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    change_log TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prd_versions_prd_id ON prd_versions(prd_id);
CREATE INDEX idx_prd_versions_version ON prd_versions(version);
CREATE UNIQUE INDEX idx_prd_versions_prd_version ON prd_versions(prd_id, version);
```

**字段说明**：
- `prd_id`: 关联的 PRD 文档 ID
- `version`: 版本号
- `change_log`: 变更日志
- `created_by`: 创建人

### 4. 测试用例表（test_cases）

存储测试用例的主要信息。

```sql
CREATE TABLE test_cases (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    prd_id VARCHAR(36) REFERENCES prd_documents(id) ON DELETE SET NULL,
    prd_version VARCHAR(20),
    module_id VARCHAR(36) REFERENCES modules(id) ON DELETE SET NULL,
    preconditions TEXT,
    expected_result TEXT NOT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'P2',
    type VARCHAR(50) NOT NULL DEFAULT 'functional',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_test_cases_prd_id ON test_cases(prd_id);
CREATE INDEX idx_test_cases_module_id ON test_cases(module_id);
CREATE INDEX idx_test_cases_priority ON test_cases(priority);
CREATE INDEX idx_test_cases_type ON test_cases(type);
CREATE INDEX idx_test_cases_status ON test_cases(status);
CREATE INDEX idx_test_cases_deleted_at ON test_cases(deleted_at);
CREATE INDEX idx_test_cases_code ON test_cases(code);
```

**字段说明**：
- `code`: 用例编号（如：TC_LOGIN_001）
- `title`: 用例标题
- `prd_id`: 关联的 PRD 文档
- `prd_version`: 关联的 PRD 版本
- `module_id`: 关联的功能模块
- `preconditions`: 前置条件
- `expected_result`: 预期结果
- `priority`: 优先级（P0/P1/P2/P3）
- `type`: 用例类型（functional/performance/compatibility/security/usability）
- `status`: 状态（active/deprecated）

### 5. 测试步骤表（test_steps）

存储测试用例的详细步骤。

```sql
CREATE TABLE test_steps (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    test_case_id VARCHAR(36) NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    action TEXT NOT NULL,
    test_data TEXT,
    expected TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_steps_test_case_id ON test_steps(test_case_id);
CREATE INDEX idx_test_steps_step_number ON test_steps(test_case_id, step_number);
```

**字段说明**：
- `test_case_id`: 关联的测试用例 ID
- `step_number`: 步骤序号
- `action`: 操作步骤描述
- `test_data`: 测试数据
- `expected`: 该步骤的预期结果

### 6. 测试步骤截图表（test_step_screenshots）

存储测试步骤的截图信息。

```sql
CREATE TABLE test_step_screenshots (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    test_step_id VARCHAR(36) NOT NULL REFERENCES test_steps(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_step_screenshots_test_step_id ON test_step_screenshots(test_step_id);
```

**字段说明**：
- `test_step_id`: 关联的测试步骤 ID
- `file_name`: 文件名
- `file_path`: 文件存储路径
- `file_size`: 文件大小（字节）
- `mime_type`: MIME 类型
- `sort_order`: 排序

### 7. 标签表（tags）

存储标签信息，用于分类和检索。

```sql
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_name ON tags(name);
```

### 8. 测试用例标签关联表（test_case_tags）

多对多关系表，关联测试用例和标签。

```sql
CREATE TABLE test_case_tags (
    test_case_id VARCHAR(36) NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    tag_id VARCHAR(36) NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (test_case_id, tag_id)
);

CREATE INDEX idx_test_case_tags_test_case_id ON test_case_tags(test_case_id);
CREATE INDEX idx_test_case_tags_tag_id ON test_case_tags(tag_id);
```

### 9. PRD 标签关联表（prd_tags）

多对多关系表，关联 PRD 和标签。

```sql
CREATE TABLE prd_tags (
    prd_id VARCHAR(36) NOT NULL REFERENCES prd_documents(id) ON DELETE CASCADE,
    tag_id VARCHAR(36) NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prd_id, tag_id)
);

CREATE INDEX idx_prd_tags_prd_id ON prd_tags(prd_id);
CREATE INDEX idx_prd_tags_tag_id ON prd_tags(tag_id);
```

### 10. 测试用例版本历史表（test_case_versions）

记录测试用例的历史版本。

```sql
CREATE TABLE test_case_versions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    test_case_id VARCHAR(36) NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    version INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    preconditions TEXT,
    expected_result TEXT NOT NULL,
    priority VARCHAR(10) NOT NULL,
    type VARCHAR(50) NOT NULL,
    change_log TEXT,
    snapshot JSONB NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_case_versions_test_case_id ON test_case_versions(test_case_id);
CREATE INDEX idx_test_case_versions_version ON test_case_versions(version);
```

**字段说明**：
- `version`: 版本号（自增）
- `snapshot`: 完整的用例快照（JSON 格式，包含步骤等）
- `change_log`: 变更说明

## Weaviate 向量数据库设计

### Collection: PRDDocuments

存储 PRD 文档的向量化数据，用于语义检索。

```json
{
  "class": "PRDDocument",
  "description": "PRD documents for semantic search",
  "vectorizer": "none",
  "properties": [
    {
      "name": "documentId",
      "dataType": ["string"],
      "description": "PostgreSQL document ID"
    },
    {
      "name": "code",
      "dataType": ["string"],
      "description": "PRD code"
    },
    {
      "name": "title",
      "dataType": ["string"],
      "description": "PRD title"
    },
    {
      "name": "version",
      "dataType": ["string"],
      "description": "PRD version"
    },
    {
      "name": "content",
      "dataType": ["text"],
      "description": "PRD content in markdown"
    },
    {
      "name": "moduleId",
      "dataType": ["string"],
      "description": "Module ID"
    },
    {
      "name": "moduleName",
      "dataType": ["string"],
      "description": "Module name"
    },
    {
      "name": "status",
      "dataType": ["string"],
      "description": "Document status"
    },
    {
      "name": "tags",
      "dataType": ["string[]"],
      "description": "Associated tags"
    },
    {
      "name": "createdAt",
      "dataType": ["date"],
      "description": "Creation timestamp"
    },
    {
      "name": "updatedAt",
      "dataType": ["date"],
      "description": "Last update timestamp"
    }
  ]
}
```

### Collection: TestCases

存储测试用例的向量化数据。

```json
{
  "class": "TestCase",
  "description": "Test cases for semantic search",
  "vectorizer": "none",
  "properties": [
    {
      "name": "caseId",
      "dataType": ["string"],
      "description": "PostgreSQL test case ID"
    },
    {
      "name": "code",
      "dataType": ["string"],
      "description": "Test case code"
    },
    {
      "name": "title",
      "dataType": ["string"],
      "description": "Test case title"
    },
    {
      "name": "prdId",
      "dataType": ["string"],
      "description": "Associated PRD ID"
    },
    {
      "name": "prdCode",
      "dataType": ["string"],
      "description": "Associated PRD code"
    },
    {
      "name": "prdVersion",
      "dataType": ["string"],
      "description": "Associated PRD version"
    },
    {
      "name": "moduleId",
      "dataType": ["string"],
      "description": "Module ID"
    },
    {
      "name": "moduleName",
      "dataType": ["string"],
      "description": "Module name"
    },
    {
      "name": "preconditions",
      "dataType": ["text"],
      "description": "Test preconditions"
    },
    {
      "name": "stepsText",
      "dataType": ["text"],
      "description": "All test steps as text"
    },
    {
      "name": "expectedResult",
      "dataType": ["text"],
      "description": "Expected result"
    },
    {
      "name": "priority",
      "dataType": ["string"],
      "description": "Priority level"
    },
    {
      "name": "type",
      "dataType": ["string"],
      "description": "Test case type"
    },
    {
      "name": "tags",
      "dataType": ["string[]"],
      "description": "Associated tags"
    },
    {
      "name": "status",
      "dataType": ["string"],
      "description": "Test case status"
    },
    {
      "name": "createdAt",
      "dataType": ["date"],
      "description": "Creation timestamp"
    },
    {
      "name": "updatedAt",
      "dataType": ["date"],
      "description": "Last update timestamp"
    }
  ]
}
```

## 数据同步策略

### PostgreSQL → Weaviate 同步

当 PostgreSQL 中的数据发生变化时，需要同步到 Weaviate：

1. **创建时**：插入新的向量对象
2. **更新时**：更新对应的向量对象
3. **删除时**：删除对应的向量对象（软删除不同步）

### 向量生成

使用 BrConnector 的 Claude 4.5 Sonnet 生成文本的 Embedding：

```go
// 伪代码
func GenerateEmbedding(text string) ([]float32, error) {
    // 调用 Claude API 生成 embedding
    // 或使用专门的 embedding 模型
}
```

## 初始化数据

### 默认模块

```sql
INSERT INTO modules (id, name, description, parent_id, sort_order) VALUES
('mod-001', '用户模块', '用户相关功能', NULL, 1),
('mod-002', '登录注册', '登录注册功能', 'mod-001', 1),
('mod-003', '个人中心', '个人信息管理', 'mod-001', 2),
('mod-004', '订单模块', '订单相关功能', NULL, 2),
('mod-005', '支付模块', '支付相关功能', NULL, 3);
```

### 默认标签

```sql
INSERT INTO tags (id, name, color, description) VALUES
('tag-001', '冒烟测试', '#f50', '核心功能冒烟测试'),
('tag-002', '回归测试', '#2db7f5', '版本回归测试'),
('tag-003', '新功能', '#87d068', '新功能测试'),
('tag-004', '缺陷验证', '#ff4d4f', '缺陷修复验证'),
('tag-005', '性能测试', '#faad14', '性能相关测试');
```

## 数据迁移

使用 GORM 的 AutoMigrate 功能或手动编写迁移脚本。

### 迁移文件示例（migrations/001_init_schema.sql）

```sql
-- 见上述所有 CREATE TABLE 语句
```

## 性能优化建议

1. **索引优化**：
   - 为常用查询字段添加索引
   - 使用复合索引优化多条件查询

2. **分区表**：
   - 如果数据量大，可以按时间分区

3. **查询优化**：
   - 使用 EXPLAIN ANALYZE 分析慢查询
   - 避免 N+1 查询问题

4. **缓存策略**：
   - 使用 Redis 缓存热点数据
   - 缓存标签列表、模块树等

## 备份策略

1. **PostgreSQL**：
   - 每日全量备份
   - 每小时增量备份（WAL）

2. **Weaviate**：
   - 定期导出向量数据
   - 可以从 PostgreSQL 重建

## 数据一致性

1. **事务处理**：
   - 使用数据库事务保证 ACID
   - 关联数据的创建/更新/删除在同一事务中

2. **最终一致性**：
   - PostgreSQL 和 Weaviate 之间采用最终一致性
   - 异步同步，失败重试

3. **数据校验**：
   - 定期校验 PostgreSQL 和 Weaviate 数据一致性
   - 提供手动同步工具
