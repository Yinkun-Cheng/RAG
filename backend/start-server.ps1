# 启动后端服务器
# 确保在 backend 目录下运行

Write-Host "Starting RAG Backend Server..." -ForegroundColor Green
Write-Host ""

# 检查配置文件
if (-not (Test-Path "config.yaml")) {
    Write-Host "Error: config.yaml not found!" -ForegroundColor Red
    Write-Host "Please make sure you are in the backend directory." -ForegroundColor Yellow
    exit 1
}

# 检查可执行文件
if (-not (Test-Path "bin/server.exe")) {
    Write-Host "Error: bin/server.exe not found!" -ForegroundColor Red
    Write-Host "Please run 'go build -o bin/server.exe ./cmd/server' first." -ForegroundColor Yellow
    exit 1
}

# 启动服务器
Write-Host "Server starting on http://localhost:8080" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

.\bin\server.exe
