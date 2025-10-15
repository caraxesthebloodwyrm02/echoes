# Deployment Guide

## Automated Deployment

### Complete Setup Script

```bash
#!/bin/bash
# Complete Docker Security Automation Suite deployment

set -euo pipefail

echo "🚀 Starting Docker Security Automation Suite deployment..."

# 1. Install dependencies
echo "📦 Installing dependencies..."
sudo apt-get update
sudo apt-get install -y curl jq docker-compose openssl

# 2. Clone repository
if [ ! -d "docker-security-automation" ]; then
    echo "📥 Cloning repository..."
    git clone <repository-url> docker-security-automation
    cd docker-security-automation
else
    echo "📂 Repository already exists, updating..."
    cd docker-security-automation
    git pull
fi

# 3. Set permissions
echo "🔐 Setting permissions..."
chmod +x *.sh
chmod +x organize-cve-reports.ps1

# 4. Generate secrets
echo "🔑 Generating secure secrets..."
./docker-security-automation-enhanced.sh 1

# 5. Configure Docker daemon (requires sudo)
echo "🐳 Configuring Docker daemon..."
sudo ./docker-security-automation-enhanced.sh 2

# 6. Enable Content Trust
echo "🔒 Enabling Docker Content Trust..."
./docker-security-automation-enhanced.sh 3

# 7. Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/organized-reports
mkdir -p logs/monthly-reports
mkdir -p security-dashboard
mkdir -p secrets
mkdir -p backups

# 8. Initial scan
echo "🔍 Performing initial security scan..."
./docker-security-automation-enhanced.sh 4

# 9. Generate dashboard
echo "📊 Generating security dashboard..."
./generate-security-dashboard.sh

# 10. Setup cron jobs
echo "⏰ Setting up scheduled tasks..."
crontab -l > cron_backup 2>/dev/null || true
echo "0 2 * * 0 /$(pwd)/docker-security-automation-enhanced.sh 4" >> cron_backup
echo "0 3 1 * * /$(pwd)/generate-security-dashboard.sh" >> cron_backup
crontab cron_backup
rm cron_backup

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review generated reports in logs/organized-reports/"
echo "2. Check security dashboard in security-dashboard/"
echo "3. Review and customize cron jobs in crontab -l"
echo "4. Test backup functionality"
echo ""
echo "🔗 Access points:"
echo "• Security Dashboard: $(pwd)/security-dashboard/"
echo "• CVE Reports: $(pwd)/logs/organized-reports/"
echo "• Documentation: $(pwd)/docs/"
```

## Manual Deployment Steps

### 1. Prerequisites Installation

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    curl \
    jq \
    docker-compose \
    openssl \
    git
```

#### CentOS/RHEL
```bash
sudo yum update -y
sudo yum install -y \
    curl \
    jq \
    docker-compose \
    openssl \
    git
```

#### macOS
```bash
brew install \
    curl \
    jq \
    docker-compose
```

### 2. Docker Configuration

#### Linux
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Verify installation
docker version
docker run hello-world
```

#### macOS
```bash
# Start Docker Desktop
open -a Docker

# Verify installation
docker version
docker run hello-world
```

### 3. Repository Setup

```bash
# Clone repository
git clone <repository-url>
cd docker-security-automation

# Set executable permissions
chmod +x *.sh
chmod +x organize-cve-reports.ps1
```

### 4. Initial Configuration

```bash
# Generate secure secrets
./docker-security-automation-enhanced.sh 1

# Configure Docker daemon (Linux)
sudo ./docker-security-automation-enhanced.sh 2

# Enable Content Trust
./docker-security-automation-enhanced.sh 3
```

## Production Deployment

### Docker Compose Integration

```yaml
version: '3.8'
services:
  security-automation:
    build: .
    volumes:
      - ./logs:/app/logs
      - ./security-dashboard:/app/security-dashboard
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DOCKER_CONTENT_TRUST=1
    restart: unless-stopped
    networks:
      - security-network

networks:
  security-network:
    driver: bridge
```

### Kubernetes Deployment

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: security-scan
spec:
  schedule: "0 2 * * 0"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: security-scan
            image: security-automation:latest
            command: ["/app/docker-security-automation-enhanced.sh", "4"]
            volumeMounts:
            - name: docker-socket
              mountPath: /var/run/docker.sock
          volumes:
          - name: docker-socket
            hostPath:
              path: /var/run/docker.sock
          restartPolicy: OnFailure
```

### CI/CD Pipeline Integration

#### GitHub Actions
```yaml
name: Security Pipeline
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Security Scan
        run: ./docker-security-automation-enhanced.sh 4
      - name: Upload Security Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: logs/
```

#### Jenkins Pipeline
```groovy
pipeline {
    agent any

    stages {
        stage('Security Scan') {
            steps {
                sh './docker-security-automation-enhanced.sh 4'
                sh './generate-security-dashboard.sh'
            }
        }

        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'logs/**/*, security-dashboard/**/*'
            }
        }
    }
}
```

## Configuration Management

### Environment-Specific Settings

#### Development
```bash
export SECURITY_LOG_LEVEL=DEBUG
export DASHBOARD_REFRESH_INTERVAL=10
export BACKUP_RETENTION_DAYS=7
```

#### Production
```bash
export SECURITY_LOG_LEVEL=WARN
export DASHBOARD_REFRESH_INTERVAL=300
export BACKUP_RETENTION_DAYS=90
```

### Secret Management

#### Using Docker Secrets
```bash
# Create secrets
echo "super-secret-password" | docker secret create db_password -

# Use in compose file
services:
  app:
    secrets:
      - db_password
```

#### Using External Secret Managers
```bash
# AWS Secrets Manager
export DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id db_password \
    --query SecretString \
    --output text)

# HashiCorp Vault
export DB_PASSWORD=$(vault kv get -field=password secret/db)
```

## Scaling and High Availability

### Multi-Node Setup

#### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy security service
docker stack deploy -c docker-compose.swarm.yml security

# Scale scanning nodes
docker service scale security_scanner=3
```

#### Kubernetes
```bash
# Deploy security application
kubectl apply -f k8s/

# Scale deployment
kubectl scale deployment security-automation --replicas=3
```

### Load Balancing

#### Nginx Configuration
```nginx
upstream security_backend {
    server security-1:8080;
    server security-2:8080;
    server security-3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://security_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### Automated Backup Strategy

```bash
#!/bin/bash
# Comprehensive backup script

BACKUP_ROOT="/backup/security-suite"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create backup directory
mkdir -p $BACKUP_ROOT/$TIMESTAMP

# Backup application files
cp -r /app/* $BACKUP_ROOT/$TIMESTAMP/

# Backup Docker data
docker run --rm \
    -v security-suite:/source \
    -v $BACKUP_ROOT/$TIMESTAMP:/backup \
    alpine tar czf /backup/docker-data.tar.gz /source

# Backup database
docker exec postgres pg_dumpall > $BACKUP_ROOT/$TIMESTAMP/postgres-backup.sql

# Create checksums
cd $BACKUP_ROOT/$TIMESTAMP
find . -type f -exec sha256sum {} \; > checksums.sha256

# Compress and encrypt
cd $BACKUP_ROOT
tar czf $TIMESTAMP.tar.gz $TIMESTAMP/
openssl aes-256-cbc -salt -in $TIMESTAMP.tar.gz -out $TIMESTAMP.enc -k $ENCRYPTION_KEY

# Cleanup
rm -rf $TIMESTAMP.tar.gz $TIMESTAMP/

# Upload to remote storage
aws s3 cp $TIMESTAMP.enc s3://security-backups/
```

### Recovery Procedures

```bash
#!/bin/bash
# Recovery script

BACKUP_FILE="20231201-120000.enc"
ENCRYPTION_KEY="your-secret-key"

# Download and decrypt
aws s3 cp s3://security-backups/$BACKUP_FILE ./
openssl aes-256-cbc -d -in $BACKUP_FILE -out backup.tar.gz -k $ENCRYPTION_KEY

# Extract backup
tar xzf backup.tar.gz

# Restore application
cp -r backup/* /app/

# Restore Docker data
cd /app
docker load < backup/docker-images.tar

# Restart services
docker-compose down
docker-compose up -d
```

## Monitoring and Alerting

### Prometheus Metrics

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'security-suite'
    static_configs:
      - targets: ['security-automation:9090']
    metrics_path: '/metrics'
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Docker Security Suite",
    "panels": [
      {
        "title": "Critical Vulnerabilities",
        "type": "stat",
        "targets": [
          {
            "expr": "cve_critical_total",
            "refId": "A"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

```yaml
groups:
  - name: security-suite
    rules:
      - alert: HighVulnerabilityCount
        expr: cve_critical_total > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High number of critical vulnerabilities detected"
```

## Troubleshooting

### Common Deployment Issues

#### Permission Denied
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Or use docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Network Issues
```bash
# Check Docker network
docker network ls

# Test connectivity
curl -I https://registry-1.docker.io

# Check firewall
sudo ufw status
sudo ufw allow 443
```

#### Resource Issues
```bash
# Check available resources
docker system df

# Clean up unused resources
./docker-security-automation-enhanced.sh 5

# Monitor resource usage
docker stats
```

### Performance Tuning

#### Memory Optimization
```bash
# Limit container memory
docker run --memory=512m --memory-swap=512m app:latest

# Optimize image layers
docker history app:latest --format "table {{.Size}}\t{{.CreatedBy}}"
```

#### Network Optimization
```bash
# Use host networking for performance
docker run --net=host app:latest

# Optimize DNS
echo 'nameserver 8.8.8.8' > /etc/docker/daemon.json.dns
```

## Support and Maintenance

### Regular Maintenance Tasks

#### Weekly
- Review security logs
- Check for new vulnerabilities
- Validate backup integrity
- Update security signatures

#### Monthly
- Generate comprehensive reports
- Review compliance status
- Update security policies
- Test disaster recovery

#### Quarterly
- Security assessment review
- Performance optimization
- Architecture review
- Team training updates

### Support Contacts

#### Technical Support
- **Email**: devops@your-company.com
- **Slack**: #docker-security
- **Jira**: DOCKERSEC project

#### Emergency Contacts
- **On-call**: +1-555-0123
- **Security**: security@your-company.com
- **Management**: management@your-company.com

---

*This deployment guide is part of the Docker Security Automation Suite.*
*For support, contact the DevOps team.*
