# Evolution Guide

This guide provides step-by-step instructions for upgrading TrajectoX systems from previous versions to the latest release.

## Prerequisites

Before starting the upgrade process, ensure you have:
- Administrative access to the target system
- Backup of current configuration and data
- Access to required credentials and secrets
- Network connectivity to all dependent services

## Version Compatibility Matrix

| Current Version | Target Version | Migration Path | Estimated Time |
|----------------|----------------|----------------|----------------|
| v1.2.x | v1.3.2 | Direct upgrade | 30 minutes |
| v1.1.x | v1.3.2 | Intermediate step required | 60 minutes |
| v1.0.x | v1.3.2 | Full migration | 120 minutes |

## Migration Steps

### Step 1: Pre-Migration Preparation

1. **Stop all services**
   ```bash
   systemctl stop trajectox-api
   systemctl stop trajectox-worker
   systemctl stop trajectox-scheduler
   ```

2. **Create backup**
   ```bash
   # Database backup
   pg_dump trajectox_db > backup_pre_migration.sql

   # Configuration backup
   cp -r /etc/trajectox /etc/trajectox.backup

   # Data directory backup
   tar -czf data_backup.tar.gz /var/lib/trajectox
   ```

3. **Verify system requirements**
   ```bash
   # Check disk space
   df -h /var/lib/trajectox

   # Check memory
   free -h

   # Check network connectivity
   curl -f https://api.github.com/repos/caraxesthebloodwyrm02/echoes/releases/latest
   ```

### Step 2: Code Deployment

1. **Clone/update repository**
   ```bash
   cd /opt/trajectox
   git fetch origin
   git checkout v1.3.2
   git submodule update --init --recursive
   ```

2. **Install dependencies**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-locked.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

### Step 3: Configuration Updates

1. **Update environment variables**
   ```bash
   # Add new Redis configuration
   echo "REDIS_URL=redis://localhost:6379/0" >> .env

   # Update monitoring endpoints
   echo "MONITORING_ENDPOINT=https://monitor.trajex.example.com/api/v1" >> .env
   ```

2. **Update service configuration**
   ```bash
   # Update systemd service files
   cp systemd/trajectox-api.service /etc/systemd/system/
   cp systemd/trajectox-worker.service /etc/systemd/system/

   # Reload systemd
   systemctl daemon-reload
   ```

### Step 4: Service Startup and Verification

1. **Start services in order**
   ```bash
   # Start database-dependent services first
   systemctl start trajectox-api
   systemctl enable trajectox-api

   # Start worker services
   systemctl start trajectox-worker
   systemctl enable trajectox-worker

   # Start scheduler
   systemctl start trajectox-scheduler
   systemctl enable trajectox-scheduler
   ```

2. **Run verification tests**
   ```bash
   # Health check
   curl -f http://localhost:8000/health

   # Basic functionality test
   python -m pytest tests/integration/test_basic_functionality.py -v

   # Performance verification
   python scripts/performance_check.py
   ```

### Step 5: Post-Migration Validation

1. **Monitor system metrics**
   ```bash
   # Check logs for errors
   journalctl -u trajectox-api -f

   # Verify metrics collection
   curl http://localhost:8000/metrics

   # Check analytics dashboard
   curl http://localhost:8000/dashboard
   ```

2. **Run full test suite**
   ```bash
   python -m pytest --cov=. --cov-report=html
   ```

## Troubleshooting

### Common Issues

#### Database Connection Failures
```bash
# Check database connectivity
psql -h localhost -U trajectox_user -d trajectox_db

# Verify connection string in .env
grep DATABASE_URL .env
```

#### Service Startup Failures
```bash
# Check service status
systemctl status trajectox-api

# View service logs
journalctl -u trajectox-api --no-pager -n 50
```

#### Performance Degradation
```bash
# Check Redis connectivity
redis-cli ping

# Verify cache configuration
python -c "import redis; r = redis.Redis(); print(r.info())"
```

### Rollback Procedures

If migration fails, rollback to previous version:

1. **Stop all services**
   ```bash
   systemctl stop trajectox-*
   ```

2. **Restore backup**
   ```bash
   # Restore database
   psql trajectox_db < backup_pre_migration.sql

   # Restore configuration
   rm -rf /etc/trajectox
   cp -r /etc/trajectox.backup /etc/trajectox

   # Restore code
   git checkout v1.3.1
   ```

3. **Restart services**
   ```bash
   systemctl start trajectox-api trajectox-worker trajectox-scheduler
   ```

## Support

For migration assistance, contact:
- **Technical Support**: support@trajex.example.com
- **Documentation**: https://docs.trajex.example.com
- **Community Forum**: https://community.trajex.example.com

## Version History

- **v1.3.2**: Current version with Redis caching and analytics dashboard
- **v1.3.1**: Previous stable version
- **v1.2.5**: Legacy version requiring intermediate migration
