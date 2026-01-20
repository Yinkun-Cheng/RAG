# 测试数据库连接脚本
Write-Host "正在测试数据库连接..." -ForegroundColor Cyan

# 检查配置文件
if (-not (Test-Path "config.yaml")) {
    Write-Host "错误: 找不到 config.yaml 文件" -ForegroundColor Red
    exit 1
}

# 编译服务器
Write-Host "正在编译服务器..." -ForegroundColor Yellow
go build -o bin/server.exe ./cmd/server
if ($LASTEXITCODE -ne 0) {
    Write-Host "编译失败" -ForegroundColor Red
    exit 1
}

Write-Host "编译成功！" -ForegroundColor Green

# 启动服务器（后台运行）
Write-Host "正在启动服务器..." -ForegroundColor Yellow
$process = Start-Process -FilePath ".\bin\server.exe" -PassThru -NoNewWindow

# 等待服务器启动
Start-Sleep -Seconds 3

# 测试健康检查端点
Write-Host "正在测试健康检查端点..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get
    Write-Host "健康检查响应:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
    
    if ($response.database -eq $true) {
        Write-Host "`n✅ 数据库连接成功！" -ForegroundColor Green
    } else {
        Write-Host "`n❌ 数据库连接失败！" -ForegroundColor Red
    }
} catch {
    Write-Host "健康检查失败: $_" -ForegroundColor Red
}

# 停止服务器
Write-Host "`n正在停止服务器..." -ForegroundColor Yellow
Stop-Process -Id $process.Id -Force
Write-Host "测试完成！" -ForegroundColor Cyan
