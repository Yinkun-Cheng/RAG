# Test script for backend server
Write-Host "Testing RAG Backend Server..." -ForegroundColor Green

# Test health endpoint
Write-Host "`nTesting /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}

# Test API v1 ping endpoint
Write-Host "`nTesting /api/v1/ping endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/ping" -Method Get
    Write-Host "✓ Ping test passed" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Ping test failed: $_" -ForegroundColor Red
}

Write-Host "`nAll tests completed!" -ForegroundColor Green
