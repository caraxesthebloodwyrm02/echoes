param([string])

Write-Host '🚀 FASTAPI + 42CRUNCH INTEGRATION EXECUTOR' -ForegroundColor Cyan
Write-Host '=========================================' -ForegroundColor Cyan

switch () {
    '1.1' {
        Write-Host '
📋 STEP 1.1: Verify Application Status' -ForegroundColor Yellow
        try {
             = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 5
            Write-Host '✅ Application is running and responding' -ForegroundColor Green
        } catch {
            Write-Host '❌ Application is not responding' -ForegroundColor Red
            Write-Host '💡 Run Step 1.2 to start the application' -ForegroundColor Yellow
        }
    }

    '1.2' {
        Write-Host '
🔧 STEP 1.2: Start FastAPI Application' -ForegroundColor Yellow
        Write-Host 'Starting FastAPI server on http://127.0.0.1:8000...' -ForegroundColor White
        try {
            Start-Process -NoNewWindow -FilePath python -ArgumentList '-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info'
            Write-Host '✅ FastAPI server started successfully' -ForegroundColor Green
            Write-Host '🌐 Access your API at: http://127.0.0.1:8000' -ForegroundColor White
            Write-Host '📚 API Documentation: http://127.0.0.1:8000/docs' -ForegroundColor White
        } catch {
            Write-Host '❌ Failed to start FastAPI server' -ForegroundColor Red
        }
    }

    '1.3' {
        Write-Host '
📥 STEP 1.3: Download OpenAPI Specification' -ForegroundColor Yellow
        try {
            Invoke-WebRequest -Uri 'http://127.0.0.1:8000/openapi.json' -OutFile 'openapi-spec.json'
            Write-Host '✅ OpenAPI specification downloaded' -ForegroundColor Green
            Write-Host '📄 File saved as: openapi-spec.json' -ForegroundColor White
            Write-Host '📊 File size:' (Get-Item 'openapi-spec.json').Length 'bytes' -ForegroundColor White
        } catch {
            Write-Host '❌ Failed to download OpenAPI spec' -ForegroundColor Red
            Write-Host '💡 Ensure Step 1.2 completed successfully' -ForegroundColor Yellow
        }
    }

    '2.3' {
        Write-Host '
🔍 STEP 2.3: 42Crunch Security Audit Instructions' -ForegroundColor Yellow
        Write-Host '📋 MANUAL STEPS REQUIRED:' -ForegroundColor Red
        Write-Host '1. Open VS Code in this project directory' -ForegroundColor White
        Write-Host '2. Install 42Crunch OpenAPI extension (if not installed)' -ForegroundColor White
        Write-Host '3. Open the openapi-spec.json file' -ForegroundColor White
        Write-Host '4. Press Ctrl+Shift+P to open command palette' -ForegroundColor White
        Write-Host '5. Type and select: \
OpenAPI:
API
Audit\' -ForegroundColor White
        Write-Host '' -ForegroundColor White
        Write-Host '🔧 Alternative commands to try:' -ForegroundColor Cyan
        Write-Host '   - \OpenAPI:
API
Scan\ (faster)' -ForegroundColor White
        Write-Host '   - \42Crunch:
Export
Scan
Report
file\' -ForegroundColor White
        Write-Host '   - \42Crunch:
Export
Audit
Report
file\' -ForegroundColor White
    }

    '3.2' {
        Write-Host '
🛡️ STEP 3.2: Run Security Scanner' -ForegroundColor Yellow
        try {
            python scripts/security_monitoring_final.py
            Write-Host '✅ Security scan completed' -ForegroundColor Green
        } catch {
            Write-Host '❌ Security scan failed' -ForegroundColor Red
        }
    }

    '4.1' {
        Write-Host '
🐳 STEP 4.1: Docker Production Build' -ForegroundColor Yellow
        Write-Host 'Building production Docker container...' -ForegroundColor White
        docker build -f Dockerfile.fastapi -t fastapi-secure:latest .
        if (18 -eq 0) {
            Write-Host '✅ Docker image built successfully' -ForegroundColor Green
        } else {
            Write-Host '❌ Docker build failed' -ForegroundColor Red
        }
    }

    'help' {
        Write-Host '
📚 AVAILABLE STEPS:' -ForegroundColor Cyan
        Write-Host '  .\integration-executor.ps1 1.1    - Check app status' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 1.2    - Start FastAPI app' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 1.3    - Download OpenAPI spec' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 2.3    - 42Crunch audit instructions' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 3.2    - Run security scanner' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 4.1    - Build Docker container' -ForegroundColor White
        Write-Host '' -ForegroundColor White
        Write-Host '🎯 RECOMMENDED SEQUENCE:' -ForegroundColor Green
        Write-Host '  1. Run 1.2 (start app)' -ForegroundColor White
        Write-Host '  2. Run 1.3 (get OpenAPI spec)' -ForegroundColor White
        Write-Host '  3. Run 2.3 (42Crunch audit)' -ForegroundColor White
        Write-Host '  4. Run 3.2 (security validation)' -ForegroundColor White
    }

    default {
        Write-Host '🚀 FastAPI + 42Crunch Integration Executor' -ForegroundColor Cyan
        Write-Host 'Usage: .\integration-executor.ps1 [step]' -ForegroundColor White
        Write-Host '' -ForegroundColor White
        Write-Host 'Examples:' -ForegroundColor Yellow
        Write-Host '  .\integration-executor.ps1 help   - Show all steps' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 1.2   - Start FastAPI app' -ForegroundColor White
        Write-Host '  .\integration-executor.ps1 1.3   - Download OpenAPI spec' -ForegroundColor White
        Write-Host '' -ForegroundColor White
        Write-Host '📋 Full workflow: See SECURITY_INTEGRATION_PLAN.md' -ForegroundColor Blue
    }
}
