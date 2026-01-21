#!/bin/bash

# 检查 Weaviate 中的 PRD 数据
# 需要 curl 和 jq 工具

WEAVIATE_URL="http://localhost:8081"

echo "=== 检查 Weaviate 连接 ==="
curl -s "${WEAVIATE_URL}/v1/meta" | jq '.'

echo ""
echo "=== 检查 PRDDocument 类 ==="
curl -s "${WEAVIATE_URL}/v1/schema/PRDDocument" | jq '.'

echo ""
echo "=== 查询所有 PRD 文档 ==="
curl -s -X POST "${WEAVIATE_URL}/v1/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{
      Get {
        PRDDocument {
          prd_id
          project_id
          title
          status
          created_at
        }
      }
    }"
  }' | jq '.'

echo ""
echo "=== 统计 PRD 文档数量 ==="
curl -s -X POST "${WEAVIATE_URL}/v1/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{
      Aggregate {
        PRDDocument {
          meta {
            count
          }
        }
      }
    }"
  }' | jq '.'
