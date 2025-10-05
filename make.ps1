param([string])

switch () {
    'build' {
        Write-Host '🔨 Building Docker image...' -ForegroundColor Green
        docker build -f Dockerfile.fastapi -t fastapi-app:latest .
    }
    'run' {
        Write-Host '🚀 Running FastAPI in development mode...' -ForegroundColor Green
        docker run -d --name fastapi-dev -p 8000:8000 fastapi-app:latest
    }
    'test' {
        Write-Host '🧪 Testing API endpoints...' -ForegroundColor Green
        bash test_api.sh
    }
    'logs' {
        Write-Host '📋 Container logs...' -ForegroundColor Green
        docker logs fastapi-dev
    }
    'stop' {
        Write-Host '⏹️  Stopping container...' -ForegroundColor Yellow
        docker stop fastapi-dev
    }
    'clean' {
        Write-Host '🗑️  Cleaning up...' -ForegroundColor Yellow
        docker stop fastapi-dev 2>
        docker rm fastapi-dev 2>
        docker rmi fastapi-app:latest 2>
    }
    'prod' {
        Write-Host '🏭 Running in production mode...' -ForegroundColor Green
        docker run -d --name fastapi-prod -p 9000:8000 -e ENVIRONMENT=production fastapi-app:latest python app/main_production.py
    }
    'install' {
        Write-Host '📦 Installing dependencies locally...' -ForegroundColor Green
        pip install -r requirements.txt
    }
    'dev' {
        Write-Host '💻 Running locally in development mode...' -ForegroundColor Green
        python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    }
    'security' {
        Write-Host '🔒 Running security scan...' -ForegroundColor Green
        python scripts/security_monitoring_final.py
    }
    default {
        Write-Host '🚀 FastAPI Docker Commands:' -ForegroundColor Cyan
        Write-Host '  .\make.ps1 build    - Build Docker image' -ForegroundColor White
        Write-Host '  .\make.ps1 run      - Run container in development mode' -ForegroundColor White
        Write-Host '  .\make.ps1 test     - Test API endpoints' -ForegroundColor White
        Write-Host '  .\make.ps1 logs     - View container logs' -ForegroundColor White
        Write-Host '  .\make.ps1 stop     - Stop running container' -ForegroundColor White
        Write-Host '  .\make.ps1 clean    - Remove container and image' -ForegroundColor White
        Write-Host '  .\make.ps1 prod     - Run in production mode' -ForegroundColor White
        Write-Host '  .\make.ps1 install  - Install dependencies locally' -ForegroundColor White
        Write-Host '  .\make.ps1 dev      - Run locally in development mode' -ForegroundColor White
        Write-Host '  .\make.ps1 security - Run security scan' -ForegroundColor White
    }
}
