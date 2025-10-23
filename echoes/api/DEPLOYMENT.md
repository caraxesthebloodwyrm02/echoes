# Echoes API - Production Deployment Guide
========================================

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your production settings
nano .env
```

### 2. Required Environment Variables
```bash
# Required for multimodal processing
OPENAI_API_KEY=sk-proj-your-openai-key-here

# API Configuration
ECHOES_API_HOST=0.0.0.0
ECHOES_API_PORT=8000
ECHOES_API_DEBUG=false

# Security - CHANGE THESE!
ECHOES_API_KEYS=prod-key-qwerty123456:1000/hour,admin-key-67890:5000/hour

# Rate Limiting
ECHOES_RATE_LIMIT_REQUESTS=1000
ECHOES_RATE_LIMIT_WINDOW=3600
```

### 3. Docker Deployment
```bash
# Build and run the API
cd echoes/api
docker-compose up -d

# Check if it's running
docker-compose ps
curl http://localhost:8000/health
```

### 4. Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run production server
python start_prod.py
```

## 🔧 API Endpoints

Once deployed, your API will be available at `http://your-server:8000`

### Core Endpoints:
- `GET /health` - Health check
- `GET /api/v1/analytics` - Usage analytics
- `POST /api/v1/analyze/image` - Image analysis
- `POST /api/v1/transcribe/audio` - Audio transcription
- `POST /api/v1/process/media` - Auto-detect processing

### Webhook Management:
- `POST /api/v1/webhooks/register` - Register webhook
- `GET /api/v1/webhooks/list` - List webhooks
- `DELETE /api/v1/webhooks/{id}` - Delete webhook

### Documentation:
- Swagger UI: `http://your-server:8000/docs`
- ReDoc: `http://your-server:8000/redoc`
- OpenAPI Schema: `http://your-server:8000/openapi.json`

## 🔒 Security Checklist

- ✅ Change default API keys
- ✅ Set strong OpenAI API key
- ✅ Configure rate limiting
- ✅ Enable CORS as needed
- ✅ Use HTTPS in production
- ✅ Monitor logs and analytics

## 📊 Monitoring

### Health Checks:
```bash
# Docker health check
docker-compose exec echoes-api curl http://localhost:8000/health

# Direct API call
curl http://your-server:8000/health
```

### Logs:
```bash
# Docker logs
docker-compose logs -f echoes-api

# Analytics
curl -H "X-API-Key: your-key" http://your-server:8000/api/v1/analytics
```

## 🔄 Scaling

### Multiple Instances:
```yaml
# docker-compose.yml
services:
  echoes-api:
    deploy:
      replicas: 3
    # ... rest of config
```

### Load Balancing:
Use nginx, Traefik, or cloud load balancers in front of multiple API instances.

## 🚨 Troubleshooting

### Common Issues:

1. **"Assistant not initialized"**
   - Check that `assistant_v2_core.py` is in the same directory
   - Ensure all dependencies are installed

2. **OpenAI API errors**
   - Verify `OPENAI_API_KEY` is set correctly
   - Check API key has sufficient credits

3. **File upload issues**
   - Check file size limits (25MB default)
   - Verify file format is supported

4. **Webhook failures**
   - Check webhook URLs are accessible
   - Verify webhook secrets match

### Logs Location:
- Docker: `docker-compose logs echoes-api`
- Manual: Check console output or configured log files

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] API keys changed from defaults
- [ ] OpenAI API key valid and funded
- [ ] HTTPS enabled (recommended)
- [ ] Monitoring/alerting set up
- [ ] Backup strategy in place
- [ ] Rate limiting configured appropriately
- [ ] CORS settings correct for your domain

---

**🎉 Your Echoes Multimodal API is now production-ready!**

For support or questions, check the main README.md or create an issue in the repository.
