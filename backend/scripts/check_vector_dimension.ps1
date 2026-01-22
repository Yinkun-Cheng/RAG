# 检查 Weaviate 中的向量维度
# 用于诊断向量维度不匹配问题

Write-Host "🔍 Checking Weaviate vector dimensions..." -ForegroundColor Cyan
Write-Host ""

# 检查 PRDDocument
Write-Host "📄 Checking PRDDocument..." -ForegroundColor Yellow
$prdQuery = @{
    query = "{ Get { PRDDocument(limit: 1) { _additional { id vector } prd_id title } } }"
} | ConvertTo-Json

try {
    $prdResult = Invoke-RestMethod -Uri "http://localhost:8009/v1/graphql" -Method Post -Body $prdQuery -ContentType "application/json"
    
    if ($prdResult.data.Get.PRDDocument -and $prdResult.data.Get.PRDDocument.Count -gt 0) {
        $vectorDim = $prdResult.data.Get.PRDDocument[0]._additional.vector.Count
        Write-Host "  ✅ PRDDocument vector dimension: $vectorDim" -ForegroundColor Green
        Write-Host "  📝 Sample PRD: $($prdResult.data.Get.PRDDocument[0].title)" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  No PRDDocument data found in Weaviate" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Failed to query PRDDocument: $_" -ForegroundColor Red
}

Write-Host ""

# 检查 TestCase
Write-Host "📋 Checking TestCase..." -ForegroundColor Yellow
$testCaseQuery = @{
    query = "{ Get { TestCase(limit: 1) { _additional { id vector } test_case_id title } } }"
} | ConvertTo-Json

try {
    $testCaseResult = Invoke-RestMethod -Uri "http://localhost:8009/v1/graphql" -Method Post -Body $testCaseQuery -ContentType "application/json"
    
    if ($testCaseResult.data.Get.TestCase -and $testCaseResult.data.Get.TestCase.Count -gt 0) {
        $vectorDim = $testCaseResult.data.Get.TestCase[0]._additional.vector.Count
        Write-Host "  ✅ TestCase vector dimension: $vectorDim" -ForegroundColor Green
        Write-Host "  📝 Sample TestCase: $($testCaseResult.data.Get.TestCase[0].title)" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  No TestCase data found in Weaviate" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Failed to query TestCase: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Expected dimensions:" -ForegroundColor Cyan
Write-Host "  - OpenAI (text-embedding-ada-002): 1536" -ForegroundColor Gray
Write-Host "  - Volcano Ark (multimodal): 2048" -ForegroundColor Gray
Write-Host "  - Mock Service: 1536" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 If dimensions don't match your current embedding provider:" -ForegroundColor Yellow
Write-Host "   1. Delete Weaviate schemas:" -ForegroundColor Gray
Write-Host "      Invoke-RestMethod -Uri 'http://localhost:8009/v1/schema/PRDDocument' -Method Delete" -ForegroundColor Gray
Write-Host "      Invoke-RestMethod -Uri 'http://localhost:8009/v1/schema/TestCase' -Method Delete" -ForegroundColor Gray
Write-Host "   2. Restart backend server (will recreate schemas)" -ForegroundColor Gray
Write-Host "   3. Re-sync data: cd backend && .\bin\sync.exe" -ForegroundColor Gray
