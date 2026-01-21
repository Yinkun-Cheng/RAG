# PowerShell 脚本：检查 Weaviate 中的 PRD 数据

$WEAVIATE_URL = "http://localhost:8081"

Write-Host "=== 检查 Weaviate 连接 ===" -ForegroundColor Green
try {
    $meta = Invoke-RestMethod -Uri "$WEAVIATE_URL/v1/meta" -Method Get
    $meta | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: 无法连接到 Weaviate" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host "`n=== 检查 PRDDocument 类 ===" -ForegroundColor Green
try {
    $schema = Invoke-RestMethod -Uri "$WEAVIATE_URL/v1/schema/PRDDocument" -Method Get
    $schema | ConvertTo-Json -Depth 10
} catch {
    Write-Host "警告: PRDDocument 类不存在或无法访问" -ForegroundColor Yellow
    Write-Host $_.Exception.Message
}

Write-Host "`n=== 查询所有 PRD 文档 ===" -ForegroundColor Green
$query = @{
    query = @"
{
  Get {
    PRDDocument {
      prd_id
      project_id
      title
      status
      created_at
    }
  }
}
"@
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$WEAVIATE_URL/v1/graphql" -Method Post -Body $query -ContentType "application/json"
    $result | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: 查询失败" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n=== 统计 PRD 文档数量 ===" -ForegroundColor Green
$countQuery = @{
    query = @"
{
  Aggregate {
    PRDDocument {
      meta {
        count
      }
    }
  }
}
"@
} | ConvertTo-Json

try {
    $countResult = Invoke-RestMethod -Uri "$WEAVIATE_URL/v1/graphql" -Method Post -Body $countQuery -ContentType "application/json"
    $countResult | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: 统计失败" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
