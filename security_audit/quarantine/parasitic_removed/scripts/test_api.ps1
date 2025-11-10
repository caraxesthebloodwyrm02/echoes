# Test Archer Framework FastAPI API
Write-Host "🌐 Testing Archer Framework FastAPI API" -ForegroundColor Green

# Test root endpoint
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
    Write-Host "✅ Root endpoint: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test metrics endpoint
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/metrics" -Method GET
    Write-Host "✅ Metrics endpoint: $($response.total_messages) messages, $($response.active_communicators) communicators" -ForegroundColor Green
} catch {
    Write-Host "❌ Metrics endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test send message endpoint
try {
    $body = @{
        content = "Hello from PowerShell!"
        receiver = "api_server"
        message_type = "network"
        priority = 8
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/send-message" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ Send message: Success=$($response.success), Time=$($response.response_time)s" -ForegroundColor Green
} catch {
    Write-Host "❌ Send message failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 API Test Complete!" -ForegroundColor Cyan
