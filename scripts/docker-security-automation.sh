#!/bin/bash

# Docker Security Automation Script
# This script automates Docker security best practices
# Usage: ./docker-security-automation.sh [step_number]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SECRETS_DIR="./secrets"
BACKUP_DIR="./backups"
LOG_FILE="./logs/docker-security.log"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create directories
mkdir -p "$SECRETS_DIR" "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

# Error handling
error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

# Warning message
warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Create secrets directory and files
create_secrets() {
    log "Creating secrets directory and files..."
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"

    # Generate secure passwords
    if command_exists openssl; then
        openssl rand -base64 32 > "$SECRETS_DIR/db_password.txt"
        openssl rand -base64 32 > "$SECRETS_DIR/redis_password.txt"
        openssl rand -base64 32 > "$SECRETS_DIR/pgadmin_password.txt"
        chmod 600 "$SECRETS_DIR"/*.txt
        success "Secrets generated and secured"
    else
        warning "OpenSSL not found. Please install it to generate secure passwords."
    fi
}

# Update Docker daemon configuration
update_docker_daemon() {
    log "Updating Docker daemon configuration..."
    local daemon_config="/etc/docker/daemon.json"

    if [[ $EUID -eq 0 ]]; then
        cat > "$daemon_config" <<EOL
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOL
        systemctl restart docker
        success "Docker daemon configuration updated and restarted"
    else
        warning "Root access required to update Docker daemon. Run with sudo."
    fi
}

# Enable Docker Content Trust
enable_content_trust() {
    log "Enabling Docker Content Trust..."
    echo 'export DOCKER_CONTENT_TRUST=1' >> ~/.bashrc
    export DOCKER_CONTENT_TRUST=1
    success "Docker Content Trust enabled"
}

# Scan for vulnerabilities
scan_images() {
    log "Scanning images for vulnerabilities..."
    if command_exists docker && docker scan --help >/dev/null 2>&1; then
        # Get all images
        local images=$(docker images --format "{{.Repository}}:{{.Tag}}")
        for image in $images; do
            log "Scanning $image..."
            docker scan "$image" || warning "Failed to scan $image"
        done
        success "Image scanning completed"
    else
        warning "Docker scan plugin not available. Install it first."
    fi
}

# Clean up unused resources
cleanup_resources() {
    log "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    success "Cleanup completed"
}

# Update images
update_images() {
    log "Updating Docker images..."
    if command_exists docker-compose; then
        docker-compose pull
        success "Images updated"
    else
        warning "docker-compose not found. Please install it."
    fi
}

# Check container security
check_security() {
    log "Checking container security..."
    if [[ $(docker ps -q) ]]; then
        docker ps --quiet | xargs docker inspect --format '{{.Id}}: SecurityOpt={{.HostConfig.SecurityOpt}}'
        success "Security check completed"
    else
        warning "No running containers to check"
    fi
}

# Set resource limits
set_resource_limits() {
    log "Setting resource limits..."
    # This would need to be implemented in docker-compose.yml
    warning "Resource limits should be set in docker-compose.yml file"
}

# Enable read-only mode
enable_readonly() {
    log "Enabling read-only mode for containers..."
    if [[ $(docker ps -q) ]]; then
        for container in $(docker ps -q); do
            docker update --read-only=true "$container" || warning "Failed to set read-only for $container"
        done
        success "Read-only mode enabled where possible"
    else
        warning "No running containers to update"
    fi
}

# Monitor container activity
monitor_containers() {
    log "Starting container monitoring..."
    if command_exists watch; then
        watch -n 2 docker stats --no-stream &
        local monitor_pid=$!
        sleep 5
        kill $monitor_pid
        success "Container monitoring completed"
    else
        warning "watch command not found"
    fi
}

# Backup important data
backup_data() {
    log "Creating data backup..."
    local backup_file="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"

    # Backup volumes
    if [[ $(docker volume ls -q) ]]; then
        for volume in $(docker volume ls -q); do
            docker run --rm -v "$volume:/source" -v "$PROJECT_ROOT:/backup" alpine tar czf "/backup/$volume-backup.tar.gz" -C /source .
        done
        success "Data backup completed"
    else
        warning "No volumes to backup"
    fi
}

# Check for secrets in images
check_secrets() {
    log "Checking for secrets in images..."
    if [[ $(docker images -q) ]]; then
        for image in $(docker images -q); do
            echo "Checking image: $image"
            docker history --no-trunc "$image" | grep -i "secret\|key\|password" || true
        done
        success "Secret check completed"
    else
        warning "No images to check"
    fi
}

# Verify network security
verify_network() {
    log "Verifying network security..."
    docker ps --format "{{.Names}}: {{.Ports}}"
    success "Network verification completed"
}

# Set up logging
setup_logging() {
    log "Setting up container logging..."
    # This would need to be implemented in docker-compose.yml
    warning "Logging configuration should be set in docker-compose.yml"
}

# Test setup
test_setup() {
    log "Testing Docker security setup..."
    if command_exists docker; then
        docker run --rm -it --net host --pid host --cap-add audit_control \
            -e DOCKER_CONTENT_TRUST=1 \
            -v /var/lib:/var/lib \
            -v /var/run/docker.sock:/var/run/docker.sock \
            --label docker_bench_security \
            docker/docker-bench-security || warning "Docker Bench Security test failed"
        success "Security test completed"
    else
        error "Docker not found"
    fi
}

# Update Docker Compose
update_docker_compose() {
    log "Updating Docker Compose..."
    if [[ $EUID -eq 0 ]]; then
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        success "Docker Compose updated"
    else
        warning "Root access required to update Docker Compose. Run with sudo."
    fi
}

# Review running services
review_services() {
    log "Reviewing running services..."
    docker ps --format "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Command}}\\t{{.Ports}}"
    success "Service review completed"
}

# Main execution
main() {
    local step="${1:-all}"

    log "Starting Docker security automation..."

    case $step in
        1) create_secrets ;;
        2) update_docker_daemon ;;
        3) enable_content_trust ;;
        4) scan_images ;;
        5) cleanup_resources ;;
        6) update_images ;;
        7) check_security ;;
        8) set_resource_limits ;;
        9) enable_readonly ;;
        10) monitor_containers ;;
        11) backup_data ;;
        12) check_secrets ;;
        13) verify_network ;;
        14) setup_logging ;;
        15) test_setup ;;
        16) update_docker_compose ;;
        17) review_services ;;
        all)
            create_secrets
            update_docker_daemon
            enable_content_trust
            scan_images
            cleanup_resources
            update_images
            check_security
            set_resource_limits
            enable_readonly
            monitor_containers
            backup_data
            check_secrets
            verify_network
            setup_logging
            test_setup
            update_docker_compose
            review_services
            ;;
        *)
            error "Invalid step. Use 1-17 or 'all'"
            ;;
    esac

    success "Docker security automation completed for step: $step"
}

# Run main function with all arguments
main "$@"
