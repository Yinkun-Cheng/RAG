# Start script for RAG Backend
Write-Host "Starting RAG Backend Server..." -ForegroundColor Green

# Check if config.yaml exists
if (-not (Test-Path "config.yaml")) {
    Write-Host "Error: config.yaml not found!" -ForegroundColor Red
    Write-Host "Please create config.yaml from config.yaml.example" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if needed
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
go mod download
go mod tidy

# Start server
Write-Host "`nStarting server on port 8080..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

go run cmd/server/main.go
