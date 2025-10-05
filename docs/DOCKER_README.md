# 🚀 Docker Development Environment

This project includes a complete Docker-based development environment with containerization support for both development and production deployments.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │   Application   │    │   Monitoring    │
│   Environment   │    │    Service      │    │    Stack        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • VS Code       │    │ • Python App    │    │ • Prometheus    │
│ • Docker Dev    │    │ • FastAPI       │    │ • Grafana       │
│ • Hot Reload    │    │ • Redis Cache   │    │ • Nginx Proxy   │
│ • Debug Tools   │    │ • PostgreSQL    │    │ • SSL/TLS       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Using Docker Scripts (Recommended)

```bash
# Start development environment
./docker-dev.sh up

# View logs
./docker-dev.sh logs

# Run tests
./docker-dev.sh test

# Run tests with coverage
./docker-dev.sh test-coverage
```

### Using PowerShell Scripts (Windows)

```powershell
# Start development environment
.\docker-dev.ps1 up

# View logs
.\docker-dev.ps1 logs

# Run tests
.\docker-dev.ps1 test
```

### Using Docker Compose Directly

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d app

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

## 🛠️ Development Workflow

### 1. Start Environment

```bash
# Start all services
./docker-dev.sh up
```

Services will be available at:
- **Application**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Health**: http://localhost:8000/health

### 2. Development

```bash
# View application logs
./docker-dev.sh logs app

# Execute commands in container
./docker-dev.sh exec app python -c "print('Hello from container!')"

# Run tests
./docker-dev.sh test

# Run tests with coverage
./docker-dev.sh test-coverage
```

### 3. Debug & Monitor

```bash
# View all container status
./docker-dev.sh status

# Monitor resource usage
docker stats

# Check service health
curl http://localhost:8000/health
```

## 🔧 VS Code Integration

### Launch Configurations

1. **Docker: Python - Current File**: Debug current Python file in container
2. **Docker: Python - Attach to Container**: Attach debugger to running container
3. **Docker: Test in Container**: Run tests inside container
4. **Docker: Debug Tests**: Debug tests with breakpoints

### Available Tasks

- **docker-build**: Build Docker image
- **docker-run: debug**: Start container for debugging
- **docker-run: test**: Run tests in container
- **docker-compose: up/down**: Manage services
- **docker-clean**: Clean up Docker resources

### Keyboard Shortcuts

- `Ctrl+Shift+P` → "Docker: Build Image"
- `Ctrl+Shift+P` → "Docker: Compose Up"
- `F5` → Start debugging in container

## 📊 Monitoring Dashboard

Access Grafana at http://localhost:3000 with credentials `admin/admin`

Pre-configured dashboards:
- **Application Metrics**: Performance and health metrics
- **Container Metrics**: CPU, memory, and disk usage
- **Custom Metrics**: Application-specific KPIs

## 🔒 Security

### Container Security

- **Multi-stage builds** for minimal attack surface
- **Non-root user** execution
- **Security scanning** with Trivy in CI/CD
- **SBOM generation** for supply chain security

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your API keys and secrets
```

## 🧪 Testing in Containers

```bash
# Run all tests
./docker-dev.sh test

# Run with coverage
./docker-dev.sh test-coverage

# Run specific test
./docker-dev.sh exec app python -m pytest tests/test_specific.py -v

# Run with debugging
./docker-dev.sh exec app python -m pytest --pdb tests/
```

## 🚀 Production Deployment

### Build Multi-Architecture Images

```bash
# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag your-registry/semantic-resonance:latest \
  --push .
```

### Deploy with Docker Compose

```yaml
version: '3.8'
services:
  app:
    image: your-registry/semantic-resonance:latest
    restart: always
    environment:
      - ENVIRONMENT=production
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `docker-compose.yml`
2. **Permission denied**: Run `docker-dev.sh clean` and restart
3. **Volume mounts**: Ensure source code is mounted correctly

### Debug Commands

```bash
# Check container logs
docker-compose logs app

# Enter container shell
docker-compose exec app bash

# View container resources
docker stats

# Check network connections
docker network ls
```

### Reset Everything

```bash
# Clean all Docker resources
./docker-dev.sh clean

# Rebuild from scratch
./docker-dev.sh down
./docker-dev.sh build
./docker-dev.sh up
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [VS Code Docker Extension](https://code.visualstudio.com/docs/containers/overview)
- [Python Docker Best Practices](https://pythonspeed.com/articles/base-image-python-docker-images/)

## 🤝 Contributing

When developing with Docker:

1. Make changes to source code (mounted volume)
2. Test changes in container
3. Commit changes to host
4. Push to trigger CI/CD pipeline
5. CI/CD will build and test new container images

---

**Happy Containerized Development!** 🐳
