#!/bin/bash
# 🚀 Echoes Production Deployment Script
# Execute with: ./deploy_production.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 ECHOES PRODUCTION DEPLOYMENT          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
REGISTRY="ghcr.io"
IMAGE_NAME="echoes-api"
CONTAINER_NAME="echoes-production"
PORT="8000"
HEALTH_ENDPOINT="http://localhost:${PORT}/health"

# Step 1: Pre-deployment Checks
echo -e "${YELLOW}[1/7]${NC} Running pre-deployment checks..."

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker is running"

# Check port is available
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Port ${PORT} is in use, stopping existing container...${NC}"
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi
echo -e "${GREEN}✓${NC} Port ${PORT} is available"

# Step 2: Build Docker Image
echo -e "\n${YELLOW}[2/7]${NC} Building Docker image..."
docker build -t ${IMAGE_NAME}:latest . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}
echo -e "${GREEN}✓${NC} Docker image built successfully"

# Step 3: Tag Image
echo -e "\n${YELLOW}[3/7]${NC} Tagging image..."
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")
docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${COMMIT_SHA}
echo -e "${GREEN}✓${NC} Image tagged: ${IMAGE_NAME}:${COMMIT_SHA}"

# Step 4: Run Container
echo -e "\n${YELLOW}[4/7]${NC} Starting production container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --restart unless-stopped \
    -p ${PORT}:8000 \
    -e ENVIRONMENT=production \
    -e LOG_LEVEL=info \
    -e OPENAI_API_KEY=${OPENAI_API_KEY:-dummy_key_for_testing} \
    --health-cmd="curl -f ${HEALTH_ENDPOINT} || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    ${IMAGE_NAME}:latest || {
        echo -e "${RED}❌ Container failed to start${NC}"
        docker logs ${CONTAINER_NAME}
        exit 1
    }
echo -e "${GREEN}✓${NC} Container started: ${CONTAINER_NAME}"

# Step 5: Wait for Health Check
echo -e "\n${YELLOW}[5/7]${NC} Waiting for application to be healthy..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -sf ${HEALTH_ENDPOINT} > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Application is healthy!"
        break
    fi

    ATTEMPT=$((ATTEMPT + 1))
    echo -ne "${YELLOW}⏳${NC} Attempt ${ATTEMPT}/${MAX_ATTEMPTS}...\r"
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "\n${RED}❌ Health check failed after ${MAX_ATTEMPTS} attempts${NC}"
    echo -e "${RED}Container logs:${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Step 6: Verify Endpoints
echo -e "\n${YELLOW}[6/7]${NC} Verifying endpoints..."

# Check health endpoint
HEALTH_RESPONSE=$(curl -s ${HEALTH_ENDPOINT})
echo -e "${GREEN}✓${NC} Health: ${HEALTH_RESPONSE}"

# Check root endpoint
ROOT_RESPONSE=$(curl -s http://localhost:${PORT}/)
echo -e "${GREEN}✓${NC} Root endpoint responding"

# Step 7: Display Status
echo -e "\n${YELLOW}[7/7]${NC} Deployment summary..."
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ DEPLOYMENT SUCCESSFUL                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Container Information:${NC}"
echo -e "   Name:      ${CONTAINER_NAME}"
echo -e "   Image:     ${IMAGE_NAME}:${COMMIT_SHA}"
echo -e "   Port:      ${PORT}"
echo -e "   Status:    $(docker inspect -f '{{.State.Status}}' ${CONTAINER_NAME})"
echo ""
echo -e "${BLUE}🌐 Endpoints:${NC}"
echo -e "   Health:    ${HEALTH_ENDPOINT}"
echo -e "   API:       http://localhost:${PORT}/api"
echo -e "   Docs:      http://localhost:${PORT}/docs"
echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "   View logs:    docker logs -f ${CONTAINER_NAME}"
echo -e "   Stop:         docker stop ${CONTAINER_NAME}"
echo -e "   Restart:      docker restart ${CONTAINER_NAME}"
echo -e "   Shell:        docker exec -it ${CONTAINER_NAME} /bin/bash"
echo ""
echo -e "${GREEN}🚀 Echoes is now running in production mode!${NC}"
echo ""

# Optional: Run smoke tests
if [ -f "tests/smoke_tests.sh" ]; then
    echo -e "${YELLOW}Running smoke tests...${NC}"
    bash tests/smoke_tests.sh
fi

exit 0
