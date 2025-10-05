#!/bin/bash
# Docker Development Workflow Script
# Provides easy commands for Docker-based development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="semantic-resonance"
DOCKER_IMAGE="${PROJECT_NAME}:dev"
COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    fi
}

# Build Docker image
build() {
    print_info "Building Docker image: $DOCKER_IMAGE"
    docker build -t $DOCKER_IMAGE .
    print_success "Docker image built successfully"
}

# Start development environment
up() {
    check_docker
    check_docker_compose

    print_info "Starting development environment..."
    docker-compose up -d
    print_success "Development environment started"

    print_info "Services available at:"
    echo "  - Application: http://localhost:8000"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Redis: localhost:6379"
    echo "  - PostgreSQL: localhost:5432"
}

# Stop development environment
down() {
    check_docker_compose

    print_info "Stopping development environment..."
    docker-compose down
    print_success "Development environment stopped"
}

# View logs
logs() {
    check_docker_compose

    if [ -n "$2" ]; then
        docker-compose logs -f $2
    else
        docker-compose logs -f app
    fi
}

# Run tests in container
test() {
    check_docker

    print_info "Running tests in Docker container..."
    docker run --rm -v $(pwd)/6/coffee_house/coffee_house:/app/coffee_house $DOCKER_IMAGE python run_tests.py
}

# Run tests with coverage
test-coverage() {
    check_docker

    print_info "Running tests with coverage in Docker container..."
    docker run --rm -v $(pwd)/6/coffee_house/coffee_house:/app/coffee_house $DOCKER_IMAGE python run_tests.py coverage
}

# Run security scan
security() {
    check_docker

    print_info "Running security scan on Docker image..."
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasecurity/trivy:latest image $DOCKER_IMAGE
}

# Clean up Docker resources
clean() {
    print_info "Cleaning up Docker resources..."

    # Stop and remove containers
    docker-compose down --volumes --remove-orphans 2>/dev/null || true

    # Remove dangling images
    docker image prune -f

    # Remove unused volumes
    docker volume prune -f

    print_success "Cleanup completed"
}

# Reset environment (down -> clean -> up)
reset_env() {
    print_info "Resetting development environment..."
    down || true
    clean
    up
}

# Show status
status() {
    check_docker_compose

    print_info "Container status:"
    docker-compose ps

    echo
    print_info "Resource usage:"
    docker stats --no-stream
}

# Execute command in running container
exec() {
    if [ -z "$2" ]; then
        print_error "Usage: ./docker-dev.sh exec <service> <command>"
        exit 1
    fi

    service=$2
    shift 2
    command="$@"

    print_info "Executing '$command' in $service container..."
    docker-compose exec $service $command
}

# Show help
help() {
    echo "Docker Development Workflow Script"
    echo
    echo "Usage: $0 <command>"
    echo
    echo "Commands:"
    echo "  build         Build Docker image"
    echo "  up            Start development environment"
    echo "  down          Stop development environment"
    echo "  logs [service] View logs (default: app)"
    echo "  test          Run tests in container"
    echo "  test-coverage Run tests with coverage"
    echo "  security      Run security scan"
    echo "  clean         Clean up Docker resources"
    echo "  reset         Reset containers (down + clean + up)"
    echo "  status        Show container status"
    echo "  exec <service> <cmd> Execute command in container"
    echo "  help          Show this help"
    echo
    echo "Examples:"
    echo "  $0 up                    # Start development environment"
    echo "  $0 logs app              # View application logs"
    echo "  $0 test                  # Run tests"
    echo "  $0 exec app python -c \"print('Hello from container!')\""
}

# Main command handler
case "${1:-help}" in
    build)
        build
        ;;
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs "$@"
        ;;
    test)
        test
        ;;
    test-coverage)
        test-coverage
        ;;
    security)
        security
        ;;
    clean)
        clean
        ;;
    reset)
        reset_env
        ;;
    status)
        status
        ;;
    exec)
        exec "$@"
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        help
        exit 1
        ;;
esac
