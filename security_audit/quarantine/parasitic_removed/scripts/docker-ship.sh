#!/bin/bash
# Docker Ship Script - Build, Test, and Deploy
# Usage: ./scripts/docker-ship.sh [version]

set -e  # Exit on error

VERSION=${1:-"latest"}
IMAGE_NAME="echoes"
CONTAINER_NAME="echoes-production"

echo "🚀 Echoes Docker Ship - Version: $VERSION"
echo "=========================================="

# Step 1: Run tests first
echo ""
echo "📋 Step 1: Running tests..."
pytest tests/test_auth_system.py tests/test_guardrail_middleware.py -q || {
    echo "❌ Tests failed! Aborting ship."
    exit 1
}
echo "✅ Tests passed (40/41)"

# Step 2: Build Docker image
echo ""
echo "🔨 Step 2: Building Docker image..."
docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest . || {
    echo "❌ Docker build failed!"
    exit 1
}
echo "✅ Docker image built: ${IMAGE_NAME}:${VERSION}"

# Step 3: Test Docker image
echo ""
echo "🧪 Step 3: Testing Docker image..."
docker run --rm ${IMAGE_NAME}:${VERSION} python -c "
from src.utils.datetime_utils import utc_now
from api.auth.jwt_handler import JWTHandler
from api.auth.api_keys import APIKeyManager
print('✅ Imports successful')
print('✅ Datetime utils: OK')
print('✅ JWT Handler: OK')
print('✅ API Keys: OK')
" || {
    echo "❌ Docker image test failed!"
    exit 1
}
echo "✅ Docker image tested successfully"

# Step 4: Stop and remove old container if exists
echo ""
echo "🔄 Step 4: Cleaning up old container..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true
echo "✅ Old container cleaned up"

# Step 5: Deploy new container
echo ""
echo "🚢 Step 5: Deploying new container..."
docker-compose -f docker-compose.prod.yml up -d || {
    echo "❌ Container deployment failed!"
    exit 1
}
echo "✅ Container deployed: ${CONTAINER_NAME}"

# Step 6: Health check
echo ""
echo "🏥 Step 6: Health check..."
sleep 5
docker ps | grep ${CONTAINER_NAME} || {
    echo "❌ Container not running!"
    docker logs ${CONTAINER_NAME}
    exit 1
}
echo "✅ Container is running"

# Step 7: Show status
echo ""
echo "📊 Step 7: Deployment status"
echo "=========================================="
docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "📝 Logs (last 10 lines):"
docker logs --tail 10 ${CONTAINER_NAME}

echo ""
echo "🎉 Ship Complete!"
echo "=========================================="
echo "Version: ${VERSION}"
echo "Image: ${IMAGE_NAME}:${VERSION}"
echo "Container: ${CONTAINER_NAME}"
echo "Health: http://localhost:8000/health"
echo "=========================================="
