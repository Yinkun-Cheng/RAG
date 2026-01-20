# 前端开发服务器启动脚本

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  启动前端开发服务器" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务器地址: http://localhost:5173" -ForegroundColor Green
Write-Host "API 代理: http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

npm run dev
