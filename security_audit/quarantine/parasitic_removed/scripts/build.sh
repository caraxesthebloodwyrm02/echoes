#!/bin/bash
# Echoes AI Build Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Echoes AI Build Script"
print_status "Project root: $PROJECT_ROOT"
echo

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Clean previous builds
print_status "Cleaning previous builds..."
cd "$PROJECT_ROOT"
rm -rf build/ dist/ *.egg-info

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Using Python $PYTHON_VERSION"

# Check if required tools are installed
print_status "Checking dependencies..."

check_tool() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
    else
        print_error "$1 is not installed"
        print_status "Installing $1..."
        pip install "$1"
    fi
}

check_tool "build"
check_tool "twine"
check_tool "wheel"

# Run tests
print_status "Running tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v
    print_success "Tests passed"
else
    print_warning "pytest not found, skipping tests"
fi

# Run linting
print_status "Running linting..."
if command -v ruff &> /dev/null; then
    ruff check .
    print_success "Linting passed"
else
    print_warning "ruff not found, skipping linting"
fi

# Build the package
print_status "Building package..."
python -m build

# Check if build was successful
if [ -d "dist" ] && [ "$(ls -A dist/)" ]; then
    print_success "Package built successfully"
    print_status "Built files:"
    ls -la dist/
else
    print_error "Build failed - no dist directory or empty dist directory"
    exit 1
fi

# Check the package
print_status "Checking package..."
twine check dist/*

if [ $? -eq 0 ]; then
    print_success "Package check passed"
else
    print_error "Package check failed"
    exit 1
fi

# Show package info
print_status "Package information:"
for file in dist/*; do
    if [ -f "$file" ]; then
        echo "  $(basename "$file"): $(du -h "$file" | cut -f1)"
    fi
done

print_success "Build process completed successfully!"
echo
print_status "Next steps:"
print_status "1. Upload to Test PyPI: python scripts/publish.py --repository testpypi"
print_status "2. Upload to PyPI: python scripts/publish.py --repository pypi"
print_status "3. Or use the build script: ./scripts/build.sh"
