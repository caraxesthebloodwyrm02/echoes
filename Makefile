# Makefile for easy Docker operations

.PHONY: build run test clean help

# Default target
help:
@echo '�� FastAPI Docker Commands:'
@echo '  make build    - Build Docker image'
@echo '  make run      - Run container in development mode'
@echo '  make test     - Test API endpoints'
@echo '  make logs     - View container logs'
@echo '  make stop     - Stop running container'
@echo '  make clean    - Remove container and image'
@echo '  make prod     - Run in production mode'

build:
@echo '🔨 Building Docker image...'
docker build -f Dockerfile.fastapi -t fastapi-app:latest .

run:
@echo '🚀 Running FastAPI in development mode...'
docker run -d --name fastapi-dev -p 8000:8000 fastapi-app:latest

test:
@echo '🧪 Testing API endpoints...'
@bash test_api.sh

logs:
@echo '📋 Container logs...'
docker logs fastapi-dev

stop:
@echo '⏹️  Stopping container...'
docker stop fastapi-dev

clean: stop
@echo '🗑️  Cleaning up...'
docker rm fastapi-dev
docker rmi fastapi-app:latest

prod:
@echo '🏭 Running in production mode...'
docker run -d --name fastapi-prod -p 9000:8000 \\
-e ENVIRONMENT=production \\
fastapi-app:latest python app/main_production.py

# Install dependencies locally (for development without Docker)
install:
@echo '📦 Installing dependencies locally...'
pip install -r requirements.txt

# Run locally (for development)
dev:
@echo '💻 Running locally in development mode...'
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Security scan
security:
@echo '🔒 Running security scan...'
python scripts/security_monitoring_final.py
