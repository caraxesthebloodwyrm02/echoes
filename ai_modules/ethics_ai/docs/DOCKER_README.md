# Docker Commands for FastAPI App

# 1. Start Docker Desktop (if not already running)

# 2. Build the Docker image
docker build -f Dockerfile.fastapi -t fastapi-app:latest .

# 3. Run in development mode
docker run -p 8000:8000 --name fastapi-dev fastapi-app:latest

# 4. Or use docker-compose for easier management
docker-compose up --build

# 5. Test the API
curl http://localhost:8000/health
curl http://localhost:8000/openapi.json

# 6. View logs
docker logs fastapi-dev

# 7. Stop the container
docker stop fastapi-dev

# 8. Remove the container
docker rm fastapi-dev

# Production mode (uncomment the api-prod service in docker-compose.yml first)
# docker-compose -f docker-compose.yml up api-prod --build

# For production deployment with security:
# - Set proper environment variables
# - Use secrets management
# - Configure HTTPS/SSL
# - Set up proper firewall rules
