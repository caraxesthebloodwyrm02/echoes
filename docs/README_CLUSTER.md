# Echoes Cluster Setup Guide

## 🚀 Overview

This guide helps you set up and manage the Echoes application cluster using Docker Compose. The cluster includes all necessary services for running Echoes in a production-like environment.

## 📋 Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Python 3.11+ (for local development)
- Git

## 🏗️ Architecture

The Echoes cluster consists of the following services:

### Core Services
- **app**: Main Echoes FastAPI application
- **nginx**: Reverse proxy and load balancer
- **postgres**: PostgreSQL database
- **redis**: Redis cache and session store

### Monitoring & Observability
- **prometheus**: Metrics collection and storage
- **grafana**: Metrics visualization and dashboards
- **jaeger**: Distributed tracing

### Networking
- **echoes-network**: Private Docker network (172.20.0.0/16)
- **Port mappings**: Services exposed on localhost

## 🛠️ Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Echoes
```

### 2. Initialize Cluster
```bash
python cluster_setup.py
```

### 3. Start Services
```bash
python cluster_start.py
```

### 4. Check Status
```bash
python cluster_status.py
```

## 🌐 Access Points

Once running, access services at:

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx Proxy**: http://localhost
- **Grafana Dashboard**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`
- **Prometheus**: http://localhost:9090
- **Jaeger Tracing**: http://localhost:16686

## 📊 Service Details

### Application (Port 8000)
- FastAPI application with all endpoints
- Health check: `/health`
- Metrics: `/metrics`
- OpenAI integration
- Agent system
- Workflow orchestration

### Nginx (Port 80/443)
- Reverse proxy for the application
- Rate limiting (10 req/s for API, 1 req/s for login)
- SSL/TLS support (configure certificates in `ssl/` directory)
- Static file serving
- WebSocket support

### PostgreSQL (Port 5432)
- Primary database
- Connection: `postgresql://echoes:echoes123@localhost:5432/echoes`
- Automatic schema initialization
- Full-text search indexes
- Monitoring schema

### Redis (Port 6379)
- Session storage
- Caching layer
- Rate limiting backend
- Background task queue

### Prometheus (Port 9090)
- Metrics collection from all services
- Custom alerts and rules
- Data retention: 200 hours
- Service discovery

### Grafana (Port 3000)
- Pre-built dashboards for Echoes
- Custom visualization panels
- Alert management
- User authentication

### Jaeger (Port 16686)
- Distributed tracing
- Performance analysis
- Service dependency mapping
- Request flow visualization

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the cluster directory:

```bash
OPENAI_API_KEY=your-openai-api-key
ENVIRONMENT=production
LOG_LEVEL=info
```

### Custom Settings
Edit configuration files in `clusters/echoes-cluster/`:

- `docker-compose.yaml`: Service definitions and scaling
- `nginx.conf`: Reverse proxy configuration
- `prometheus.yml`: Metrics collection rules
- `init-db.sql`: Database schema and sample data

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale application to 3 instances
docker-compose -f clusters/echoes-cluster/docker-compose.yaml up -d --scale app=3
```

### Resource Limits
Adjust resource limits in `docker-compose.yaml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🔒 Security

### Network Security
- Services communicate within private Docker network
- Only necessary ports exposed to host
- Nginx provides additional security layer

### Authentication
- Grafana: Default credentials (change in production)
- Database: Encrypted password storage
- API: Optional API key authentication

### SSL/TLS
1. Place certificates in `ssl/` directory:
   - `cert.pem`: SSL certificate
   - `key.pem`: Private key

2. Uncomment HTTPS block in `nginx.conf`

## 📝 Monitoring

### Key Metrics
- Application response times
- Database connection pool
- Redis memory usage
- Request rates and errors
- System resource utilization

### Alerts
Configure alerts in Prometheus or Grafana for:
- High error rates
- Resource exhaustion
- Service downtime
- Performance degradation

## 🛠️ Management Commands

### Start/Stop
```bash
# Start all services
docker-compose -f clusters/echoes-cluster/docker-compose.yaml up -d

# Stop all services
docker-compose -f clusters/echoes-cluster/docker-compose.yaml down

# Restart specific service
docker-compose -f clusters/echoes-cluster/docker-compose.yaml restart app
```

### Logs
```bash
# View all logs
docker-compose -f clusters/echoes-cluster/docker-compose.yaml logs -f

# View specific service logs
docker-compose -f clusters/echoes-cluster/docker-compose.yaml logs -f app

# View last 100 lines
docker-compose -f clusters/echoes-cluster/docker-compose.yaml logs --tail=100 app
```

### Maintenance
```bash
# Update images
docker-compose -f clusters/echoes-cluster/docker-compose.yaml pull

# Clean up unused resources
docker system prune -f

# Backup database
docker exec echoes-postgres pg_dump -U echoes echoes > backup.sql
```

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**
   - Check if ports are already in use
   - Modify port mappings in `docker-compose.yaml`

2. **Memory issues**
   - Increase Docker Desktop memory allocation
   - Adjust service memory limits

3. **Database connection errors**
   - Verify PostgreSQL is running
   - Check connection string in environment

4. **High resource usage**
   - Monitor with `docker stats`
   - Scale down unnecessary services
   - Optimize application performance

### Health Checks
```bash
# Check individual service health
curl http://localhost:8000/health
curl http://localhost/health
curl http://localhost:3000/api/health
```

### Debug Mode
```bash
# Run with debug logging
ENVIRONMENT=development LOG_LEVEL=debug docker-compose up
```

## 🚀 Production Deployment

### Before Production
1. Change default passwords
2. Configure SSL/TLS certificates
3. Set up proper monitoring and alerts
4. Configure backup strategies
5. Review security settings

### Performance Tuning
1. Optimize database queries
2. Configure connection pooling
3. Enable HTTP/2 in Nginx
4. Set up CDN for static assets
5. Configure caching strategies

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs for error messages
3. Verify Docker Desktop is running properly
4. Check system resources (memory, disk space)

For additional help, create an issue in the project repository.
