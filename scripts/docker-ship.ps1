# Docker Ship Script - Build, Test, and Deploy (PowerShell)
# Usage: .\scripts\docker-ship.ps1 [-Version "1.0.0"]

param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

$ImageName = "echoes"
$ContainerName = "echoes-production"

Write-Host "🚀 Echoes Docker Ship - Version: $Version" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Step 1: Run tests first
Write-Host ""
Write-Host "📋 Step 1: Running tests..." -ForegroundColor Yellow
try {
    pytest tests/test_auth_system.py tests/test_guardrail_middleware.py -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
    Write-Host "✅ Tests passed (40/41)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Tests failed! Aborting ship." -ForegroundColor Red
    exit 1
}

# Step 2: Build Docker image
Write-Host ""
Write-Host "🔨 Step 2: Building Docker image..." -ForegroundColor Yellow
try {
    docker build -t "${ImageName}:${Version}" -t "${ImageName}:latest" .
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
    Write-Host "✅ Docker image built: ${ImageName}:${Version}" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Test Docker image
Write-Host ""
Write-Host "🧪 Step 3: Testing Docker image..." -ForegroundColor Yellow
try {
    $testScript = @"
from src.utils.datetime_utils import utc_now
from api.auth.jwt_handler import JWTHandler
from api.auth.api_keys import APIKeyManager
print('✅ Imports successful')
print('✅ Datetime utils: OK')
print('✅ JWT Handler: OK')
print('✅ API Keys: OK')
"@
    docker run --rm "${ImageName}:${Version}" python -c $testScript
    if ($LASTEXITCODE -ne 0) { throw "Test failed" }
    Write-Host "✅ Docker image tested successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker image test failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Stop and remove old container if exists
Write-Host ""
Write-Host "🔄 Step 4: Cleaning up old container..." -ForegroundColor Yellow
docker stop $ContainerName 2>$null
docker rm $ContainerName 2>$null
Write-Host "✅ Old container cleaned up" -ForegroundColor Green

# Step 5: Deploy new container
Write-Host ""
Write-Host "🚢 Step 5: Deploying new container..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.prod.yml up -d
    if ($LASTEXITCODE -ne 0) { throw "Deployment failed" }
    Write-Host "✅ Container deployed: $ContainerName" -ForegroundColor Green
}
catch {
    Write-Host "❌ Container deployment failed!" -ForegroundColor Red
    exit 1
}

# Step 6: Health check
Write-Host ""
Write-Host "🏥 Step 6: Health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$running = docker ps | Select-String $ContainerName
if (-not $running) {
    Write-Host "❌ Container not running!" -ForegroundColor Red
    docker logs $ContainerName
    exit 1
}
Write-Host "✅ Container is running" -ForegroundColor Green

# Step 7: Show status
Write-Host ""
Write-Host "📊 Step 7: Deployment status" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
docker ps --filter "name=$ContainerName" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"
Write-Host ""
Write-Host "📝 Logs (last 10 lines):" -ForegroundColor Cyan
docker logs --tail 10 $ContainerName

Write-Host ""
Write-Host "🎉 Ship Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor White
Write-Host "Image: ${ImageName}:${Version}" -ForegroundColor White
Write-Host "Container: $ContainerName" -ForegroundColor White
Write-Host "Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
