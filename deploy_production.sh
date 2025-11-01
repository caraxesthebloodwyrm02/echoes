#!/bin/bash
# Echoes Assistant V2 Production Deployment Script
# OpenAI Responses API Migration Rollout

set -e

echo "Starting Echoes Assistant V2 Production Deployment"
echo "=================================================="

# Configuration
DEPLOYMENT_DIR="/opt/echoes_assistant"
CONFIG_DIR="$DEPLOYMENT_DIR/config"
BACKUP_DIR="$DEPLOYMENT_DIR/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Pre-deployment checks
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if deployment directory exists
    if [ ! -d "$DEPLOYMENT_DIR" ]; then
        error "Deployment directory $DEPLOYMENT_DIR does not exist"
        exit 1
    fi

    # Check for required environment variables
    if [ -z "$OPENAI_API_KEY" ]; then
        error "OPENAI_API_KEY environment variable not set"
        exit 1
    fi

    log "Prerequisites check completed"
}

# Backup current deployment
create_backup() {
    log "Creating backup..."

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

    mkdir -p "$BACKUP_PATH"

    # Backup configuration
    if [ -d "$CONFIG_DIR" ]; then
        cp -r "$CONFIG_DIR" "$BACKUP_PATH/"
    fi

    # Backup application code
    if [ -f "$DEPLOYMENT_DIR/assistant_v2_core.py" ]; then
        cp "$DEPLOYMENT_DIR/assistant_v2_core.py" "$BACKUP_PATH/"
    fi

    log "Backup created: $BACKUP_PATH"
}

# Deploy new version
deploy_application() {
    log "Deploying application..."

    # Copy new files
    cp assistant_v2_core.py "$DEPLOYMENT_DIR/"
    cp -r config/* "$CONFIG_DIR/" 2>/dev/null || true

    # Set permissions
    chmod 644 "$DEPLOYMENT_DIR/assistant_v2_core.py"
    chmod 600 "$CONFIG_DIR"/*.json 2>/dev/null || true

    log "Application deployed successfully"
}

# Configure feature flags
configure_rollout() {
    local rollout_percentage=$1

    log "Configuring rollout: ${rollout_percentage}%"

    # Set environment variables
    cat > "$DEPLOYMENT_DIR/.env" << EOF
OPENAI_API_KEY=$OPENAI_API_KEY
USE_RESPONSES_API=true
USE_RESPONSES_API_ROLLOUT=$rollout_percentage
EOF

    log "Rollout configured: ${rollout_percentage}%"
}

# Health check
health_check() {
    log "Performing health check..."

    # Basic syntax check
    if ! python3 -m py_compile "$DEPLOYMENT_DIR/assistant_v2_core.py"; then
        error "Syntax check failed"
        return 1
    fi

    log "Health check passed"
    return 0
}

# Rollback function
rollback() {
    log "Initiating rollback..."

    LAST_BACKUP=$(cat "$DEPLOYMENT_DIR/last_backup" 2>/dev/null)
    if [ -z "$LAST_BACKUP" ] || [ ! -d "$LAST_BACKUP" ]; then
        error "No backup found for rollback"
        exit 1
    fi

    # Restore files
    if [ -f "$LAST_BACKUP/assistant_v2_core.py" ]; then
        cp "$LAST_BACKUP/assistant_v2_core.py" "$DEPLOYMENT_DIR/"
    fi

    if [ -d "$LAST_BACKUP/config" ]; then
        cp -r "$LAST_BACKUP/config" "$CONFIG_DIR/"
    fi

    log "Rollback completed successfully"
}

# Main deployment function
deploy() {
    local rollout_percentage=${1:-10}

    echo "Starting deployment with ${rollout_percentage}% rollout..."

    check_prerequisites
    create_backup
    deploy_application
    configure_rollout "$rollout_percentage"

    if health_check; then
        log "Deployment completed successfully!"
        log "Monitoring rollout at ${rollout_percentage}% capacity"
        log "Use 'rollback' command if issues arise"
    else
        error "Health check failed, initiating rollback..."
        rollback
        exit 1
    fi
}

# Command line interface
case "${1:-deploy}" in
    "deploy")
        deploy "${2:-10}"
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 [deploy <percentage>|rollback|health]"
        echo "  deploy <percentage>  - Deploy with specified rollout percentage (default: 10)"
        echo "  rollback             - Rollback to previous version"
        echo "  health              - Run health checks"
        exit 1
        ;;
esac
