# 清空 Weaviate 并重新同步数据
# 用于解决向量维度不匹配问题

Write-Host "⚠️  WARNING: This will delete all data in Weaviate!" -ForegroundColor Red
Write-Host "Press Ctrl+C to cancel, or any other key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "🗑️  Deleting Weaviate schemas..." -ForegroundColor Cyan

# 删除 PRDDocument schema
try {
    Invoke-RestMethod -Uri "http://localhost:8009/v1/schema/PRDDocument" -Method Delete
    Write-Host "  ✅ PRDDocument schema deleted" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  PRDDocument schema not found or already deleted" -ForegroundColor Yellow
}

# 删除 TestCase schema
try {
    Invoke-RestMethod -Uri "http://localhost:8009/v1/schema/TestCase" -Method Delete
    Write-Host "  ✅ TestCase schema deleted" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  TestCase schema not found or already deleted" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Weaviate schemas deleted successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart backend server (it will recreate schemas automatically)" -ForegroundColor Gray
Write-Host "  2. Run sync command: cd backend && .\bin\sync.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 The new data will use the current embedding provider's dimension" -ForegroundColor Yellow
