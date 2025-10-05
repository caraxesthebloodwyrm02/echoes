# 🚀 QUICK LAUNCH - FASTAPI + 42CRUNCH SETUP

Write-Host '🚀 FASTAPI + 42CRUNCH QUICK LAUNCH' -ForegroundColor Cyan
Write-Host '=================================' -ForegroundColor Cyan

# Step 1: Check/Start Application
Write-Host '
1. Starting FastAPI Application...' -ForegroundColor Yellow
try {
    Start-Process -NoNewWindow -FilePath python -ArgumentList '-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info'
    Write-Host '✅ FastAPI server starting...' -ForegroundColor Green
} catch {
    Write-Host '❌ Failed to start FastAPI server' -ForegroundColor Red
    exit 1
}

# Step 2: Wait and verify
Write-Host '
2. Waiting for application to start...' -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 3: Download OpenAPI spec
Write-Host '
3. Downloading OpenAPI specification...' -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri 'http://127.0.0.1:8000/openapi.json' -OutFile 'openapi-spec.json'
    Write-Host '✅ OpenAPI spec downloaded successfully' -ForegroundColor Green
} catch {
    Write-Host '❌ Failed to download OpenAPI spec' -ForegroundColor Red
}

# Step 4: Instructions
Write-Host '
🎯 READY FOR 42CRUNCH AUDIT!' -ForegroundColor Green
Write-Host '=============================' -ForegroundColor Green
Write-Host '' -ForegroundColor White
Write-Host '📋 Next Steps:' -ForegroundColor Yellow
Write-Host '1. Open VS Code in this project directory' -ForegroundColor White
Write-Host '2. Install 42Crunch OpenAPI extension (if needed)' -ForegroundColor White
Write-Host '3. Open the openapi-spec.json file' -ForegroundColor White
Write-Host '4. Press Ctrl+Shift+P and type: \
OpenAPI:
API
Audit\' -ForegroundColor White
Write-Host '' -ForegroundColor White
Write-Host '🔧 Alternative quick commands:' -ForegroundColor Cyan
Write-Host '   - Ctrl+Shift+P → \OpenAPI:
API
Scan\' -ForegroundColor White
Write-Host '   - Ctrl+Shift+P → \42Crunch:
Export
Scan
Report\' -ForegroundColor White
Write-Host '' -ForegroundColor White
Write-Host '📊 Your API endpoints to audit:' -ForegroundColor Blue
Write-Host '   • Authentication: /api/auth/login, /api/auth/me' -ForegroundColor White
Write-Host '   • System Health: /health, /metrics' -ForegroundColor White
Write-Host '   • Finance APIs: /api/finance/*' -ForegroundColor White
Write-Host '' -ForegroundColor White
Write-Host '🌐 API Documentation: http://127.0.0.1:8000/docs' -ForegroundColor Green
Write-Host '📄 OpenAPI Spec: openapi-spec.json' -ForegroundColor Green
Write-Host '' -ForegroundColor White
Write-Host '✨ Ready for professional security auditing!' -ForegroundColor Green
