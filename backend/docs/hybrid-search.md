# 混合检索（Hybrid Search）使用指南

## 什么是混合检索？

混合检索是一种结合了**向量检索**（语义相似度）和**关键词检索**（BM25/全文检索）的搜索方式。它可以同时利用两种检索方式的优势：

- **向量检索**：基于语义理解，能找到意思相近但用词不同的内容
- **关键词检索（BM25）**：基于关键词匹配，能精确找到包含特定词汇的内容

## Alpha 参数说明

`alpha` 参数控制两种检索方式的权重，取值范围为 0-1：

- **alpha = 0**：纯 BM25 关键词检索
- **alpha = 0.5**：向量检索和 BM25 各占 50%
- **alpha = 1**：纯向量检索（默认值）

### 推荐配置

| 场景 | alpha 值 | 说明 |
|------|---------|------|
| 精确匹配 | 0 - 0.3 | 适合查找包含特定关键词的文档 |
| 平衡模式 | 0.4 - 0.6 | 兼顾语义理解和关键词匹配 |
| 语义搜索 | 0.7 - 1.0 | 适合理解用户意图，找到语义相关的内容 |

## API 使用示例

### 1. 纯向量检索（默认）

```json
POST /api/v1/projects/:id/search
{
  "query": "用户登录功能",
  "type": "all",
  "limit": 10
}
```

或显式指定 alpha = 1：

```json
{
  "query": "用户登录功能",
  "type": "all",
  "limit": 10,
  "alpha": 1.0
}
```

### 2. 混合检索（推荐）

```json
POST /api/v1/projects/:id/search
{
  "query": "用户登录功能",
  "type": "all",
  "limit": 10,
  "alpha": 0.5
}
```

### 3. 纯关键词检索

```json
POST /api/v1/projects/:id/search
{
  "query": "用户登录功能",
  "type": "all",
  "limit": 10,
  "alpha": 0.0
}
```

## 完整请求参数

```json
{
  "query": "搜索查询文本",           // 必填：搜索关键词
  "type": "all",                     // 必填：搜索类型（prd/testcase/all）
  "limit": 10,                       // 可选：结果数量限制（默认 10）
  "score_threshold": 0.7,            // 可选：相似度阈值（默认 0.7）
  "alpha": 0.5,                      // 可选：混合检索权重（默认 1.0）
  "project_id": "xxx",               // 可选：项目ID过滤
  "module_id": "xxx",                // 可选：模块ID过滤
  "app_version_id": "xxx",           // 可选：版本ID过滤
  "status": "active",                // 可选：状态过滤
  "include_archived": false          // 可选：是否包含已归档
}
```

## 使用建议

### 1. 根据查询类型选择 alpha

- **精确查询**（如 "PRD-001"、"登录按钮"）：使用较低的 alpha（0.2-0.4）
- **模糊查询**（如 "如何实现用户认证"）：使用较高的 alpha（0.6-0.8）
- **语义查询**（如 "提升系统安全性的方案"）：使用 alpha = 1.0

### 2. 性能考虑

- 纯向量检索（alpha = 1.0）性能最好
- 混合检索会略微增加计算开销
- 纯 BM25（alpha = 0.0）性能也很好，但语义理解能力较弱

### 3. 结果质量

- 混合检索通常能提供最好的结果质量
- 建议从 alpha = 0.5 开始测试，根据实际效果调整

## 技术实现

### 后端实现

1. **搜索服务**：`backend/internal/service/search/search_service.go`
   - 根据 alpha 值选择检索方式
   - 默认 alpha = 1.0（纯向量检索）

2. **Weaviate 客户端**：`backend/internal/pkg/weaviate/client.go`
   - `SearchPRDs/SearchTestCases`：纯向量检索
   - `HybridSearchPRDs/HybridSearchTestCases`：混合检索

### Weaviate 配置

混合检索需要 Weaviate 支持 BM25 索引。当前配置已自动启用：

```yaml
# Schema 配置中的 invertedIndexConfig
invertedIndexConfig:
  bm25:
    b: 0.75
    k1: 1.2
```

## 常见问题

### Q: 为什么混合检索结果和纯向量检索不同？

A: 混合检索会考虑关键词匹配，因此包含查询关键词的文档会获得更高的分数。

### Q: 如何选择最佳的 alpha 值？

A: 建议通过 A/B 测试来确定。一般来说，alpha = 0.5 是一个不错的起点。

### Q: 混合检索是否支持中文？

A: 是的，Weaviate 的 BM25 支持中文分词，可以正确处理中文查询。

### Q: 可以动态调整 alpha 吗？

A: 可以。每次请求都可以指定不同的 alpha 值，非常灵活。

## 示例代码

### JavaScript/TypeScript

```typescript
// 混合检索示例
const searchResults = await fetch('/api/v1/projects/123/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: '用户登录功能',
    type: 'all',
    limit: 10,
    alpha: 0.5  // 混合检索
  })
});

const data = await searchResults.json();
console.log(data.results);
```

### Python

```python
import requests

# 混合检索示例
response = requests.post(
    'http://localhost:8080/api/v1/projects/123/search',
    json={
        'query': '用户登录功能',
        'type': 'all',
        'limit': 10,
        'alpha': 0.5  # 混合检索
    }
)

results = response.json()['results']
for result in results:
    print(f"{result['title']} - Score: {result['score']}")
```

## 参考资料

- [Weaviate Hybrid Search 文档](https://weaviate.io/developers/weaviate/search/hybrid)
- [BM25 算法介绍](https://en.wikipedia.org/wiki/Okapi_BM25)
- [向量检索 vs 关键词检索](https://weaviate.io/blog/vector-search-vs-keyword-search)
