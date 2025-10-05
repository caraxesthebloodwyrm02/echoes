# 42Crunch OpenAPI Security Audit Workflow
# ========================================

Write-Host '🚀 42Crunch OpenAPI Security Audit Setup' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

# Step 1: Verify API is running
Write-Host '
1. Checking API Status...' -ForegroundColor Yellow
try {
     = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 5
    Write-Host '✅ API is running and responding' -ForegroundColor Green
} catch {
    Write-Host '❌ API is not responding. Please start the FastAPI app first.' -ForegroundColor Red
    exit 1
}

# Step 2: Download OpenAPI spec
Write-Host '
2. Downloading OpenAPI Specification...' -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri 'http://127.0.0.1:8000/openapi.json' -OutFile 'openapi-spec.json'
    Write-Host '✅ OpenAPI spec saved to openapi-spec.json' -ForegroundColor Green
} catch {
    Write-Host '❌ Failed to download OpenAPI spec' -ForegroundColor Red
}

# Step 3: Instructions for 42Crunch
Write-Host '
3. 42Crunch Security Audit Instructions:' -ForegroundColor Yellow
Write-Host '   📋 Open VS Code with 42Crunch extension installed' -ForegroundColor White
Write-Host '   📁 Open the openapi-spec.json file' -ForegroundColor White
Write-Host '   ⌨️  Press Ctrl+Shift+P to open command palette' -ForegroundColor White
Write-Host '' -ForegroundColor White
Write-Host '   🔍 Run Security Audit:' -ForegroundColor Cyan
Write-Host '      Type: \
OpenAPI:
API
Audit\ and select it' -ForegroundColor White
Write-Host '' -ForegroundColor White
Write-Host '   📊 Export Security Report:' -ForegroundColor Cyan
Write-Host '      Type: \42Crunch:
Export
Scan
Report
file\ and select it' -ForegroundColor White
Write-Host '' -ForegroundColor White
Write-Host '   🔒 Alternative Commands:' -ForegroundColor Cyan
Write-Host '      - \OpenAPI:
API
Scan\ for quick scanning' -ForegroundColor White
Write-Host '      - \42Crunch:
Export
Audit
Report
file\ for detailed audit' -ForegroundColor White

Write-Host '
4. Manual Security Checks:' -ForegroundColor Yellow
Write-Host '   📝 Your API endpoints to review:' -ForegroundColor White
Write-Host '      • POST /api/auth/login' -ForegroundColor White
Write-Host '      • GET  /api/auth/me' -ForegroundColor White
Write-Host '      • GET  /health' -ForegroundColor White
Write-Host '      • GET  /metrics' -ForegroundColor White

Write-Host '
🎯 Next Steps:' -ForegroundColor Green
Write-Host '1. Open openapi-spec.json in VS Code' -ForegroundColor White
Write-Host '2. Run the 42Crunch security audit' -ForegroundColor White
Write-Host '3. Review and fix any security issues found' -ForegroundColor White
Write-Host '4. Export the security report' -ForegroundColor White

Write-Host '
📚 Useful Links:' -ForegroundColor Blue
Write-Host '• 42Crunch Extension: https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi' -ForegroundColor White
Write-Host '• OpenAPI Security Best Practices: https://42crunch.com/' -ForegroundColor White

Write-Host '
✨ Ready for 42Crunch security auditing!' -ForegroundColor Green
