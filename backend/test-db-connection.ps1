# Test Database Connection Script
Write-Host "Testing database connection..." -ForegroundColor Cyan

# Check config file
if (-not (Test-Path "config.yaml")) {
    Write-Host "Error: config.yaml not found" -ForegroundColor Red
    exit 1
}

# Build server
Write-Host "Building server..." -ForegroundColor Yellow
go build -o bin/server.exe ./cmd/server
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Build successful!" -ForegroundColor Green

# Start server (background)
Write-Host "Starting server..." -ForegroundColor Yellow
$process = Start-Process -FilePath ".\bin\server.exe" -PassThru -NoNewWindow

# Wait for server to start
Start-Sleep -Seconds 3

# Test health check endpoint
Write-Host "Testing health check endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get
    Write-Host "Health check response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
    
    if ($response.database -eq $true) {
        Write-Host "`nDatabase connection successful!" -ForegroundColor Green
    } else {
        Write-Host "`nDatabase connection failed!" -ForegroundColor Red
    }
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
}

# Stop server
Write-Host "`nStopping server..." -ForegroundColor Yellow
Stop-Process -Id $process.Id -Force
Write-Host "Test completed!" -ForegroundColor Cyan
