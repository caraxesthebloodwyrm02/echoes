#!/bin/bash
# Echoes AI Release Script

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

print_status "Echoes AI Release Script"
print_status "Project root: $PROJECT_ROOT"
echo

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Parse command line arguments
DRY_RUN=false
SKIP_TESTS=false
SKIP_LINTING=false
REPOSITORY="testpypi"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|-d)
            DRY_RUN=true
            shift
            ;;
        --skip-tests|-t)
            SKIP_TESTS=true
            shift
            ;;
        --skip-linting|-l)
            SKIP_LINTING=true
            shift
            ;;
        --repository|-r)
            REPOSITORY="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --dry-run, -d        Build package but don't upload"
            echo "  --skip-tests, -t     Skip running tests"
            echo "  --skip-linting, -l   Skip running linting"
            echo "  --repository, -r     Repository to publish to (testpypi, pypi, both)"
            echo "  --help, -h           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_status "Release configuration:"
print_status "  Dry run: $DRY_RUN"
print_status "  Skip tests: $SKIP_TESTS"
print_status "  Skip linting: $SKIP_LINTING"
print_status "  Repository: $REPOSITORY"
echo

# Check if git is clean
print_status "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    print_error "Git working directory is not clean"
    print_status "Please commit or stash changes before releasing"
    exit 1
fi

# Get current version
print_status "Getting current version..."
CURRENT_VERSION=$(python -c "
import sys
sys.path.insert(0, '.')
from echoes import __version__
print(__version__)
")
print_status "Current version: $CURRENT_VERSION"

# Check if tag exists
if git rev-parse "v$CURRENT_VERSION" >/dev/null 2>&1; then
    print_warning "Tag v$CURRENT_VERSION already exists"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Release cancelled"
        exit 0
    fi
fi

# Run tests
if [ "$SKIP_TESTS" = false ]; then
    print_status "Running tests..."
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
        print_success "Tests passed"
    else
        print_warning "pytest not found, skipping tests"
    fi
else
    print_warning "Skipping tests"
fi

# Run linting
if [ "$SKIP_LINTING" = false ]; then
    print_status "Running linting..."
    if command -v ruff &> /dev/null; then
        ruff check .
        print_success "Linting passed"
    else
        print_warning "ruff not found, skipping linting"
    fi
else
    print_warning "Skipping linting"
fi

# Build package
print_status "Building package..."
python -m build

# Check package
print_status "Checking package..."
twine check dist/*

if [ $? -eq 0 ]; then
    print_success "Package check passed"
else
    print_error "Package check failed"
    exit 1
fi

# Show built files
print_status "Built files:"
ls -la dist/

# Upload to repository
if [ "$DRY_RUN" = false ]; then
    case $REPOSITORY in
        testpypi)
            print_status "Uploading to Test PyPI..."
            python scripts/publish.py --repository testpypi --skip-tests --skip-linting
            ;;
        pypi)
            print_status "Uploading to PyPI..."
            python scripts/publish.py --repository pypi --skip-tests --skip-linting
            ;;
        both)
            print_status "Uploading to Test PyPI..."
            python scripts/publish.py --repository testpypi --skip-tests --skip-linting
            
            print_status "Uploading to PyPI..."
            read -p "Continue with production PyPI upload? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                python scripts/publish.py --repository pypi --skip-tests --skip-linting
            else
                print_status "Skipping production PyPI upload"
            fi
            ;;
        *)
            print_error "Unknown repository: $REPOSITORY"
            exit 1
            ;;
    esac
else
    print_status "Dry run - skipping upload"
fi

# Create git tag
if [ "$DRY_RUN" = false ]; then
    print_status "Creating git tag..."
    git tag -a "v$CURRENT_VERSION" -m "Release version $CURRENT_VERSION"
    git push origin "v$CURRENT_VERSION"
    print_success "Git tag created and pushed"
else
    print_status "Dry run - skipping git tag"
fi

# Create GitHub release (if gh CLI is available)
if command -v gh &> /dev/null && [ "$DRY_RUN" = false ]; then
    print_status "Creating GitHub release..."
    
    # Generate release notes
    RELEASE_NOTES="Echoes AI v$CURRENT_VERSION

## Installation
\`\`\`bash
pip install echoes-ai
\`\`\`

## Features
- Multi-agent conversation management
- OpenAI and Anthropic AI integration
- Workflow orchestration
- Media search and classification
- Real-time chat and API endpoints
- Comprehensive monitoring and observability

## Documentation
- API Documentation: https://echoes-ai.readthedocs.io
- GitHub Repository: https://github.com/echoes-ai/echoes

## Changes
See CHANGELOG.md for detailed changes.
"
    
    echo "$RELEASE_NOTES" | gh release create "v$CURRENT_VERSION" --title "Echoes AI v$CURRENT_VERSION" --notes-file -
    print_success "GitHub release created"
else
    if [ "$DRY_RUN" = false ]; then
        print_warning "gh CLI not found, skipping GitHub release"
    else
        print_status "Dry run - skipping GitHub release"
    fi
fi

print_success "Release process completed successfully!"
echo

if [ "$DRY_RUN" = false ]; then
    print_status "Release summary:"
    print_status "  Version: $CURRENT_VERSION"
    print_status "  Repository: $REPOSITORY"
    print_status "  Git tag: v$CURRENT_VERSION"
    
    if [ "$REPOSITORY" = "testpypi" ] || [ "$REPOSITORY" = "both" ]; then
        print_status "  Test PyPI: pip install --index-url https://test.pypi.org/simple/ echoes-ai"
    fi
    
    if [ "$REPOSITORY" = "pypi" ] || [ "$REPOSITORY" = "both" ]; then
        print_status "  PyPI: pip install echoes-ai"
    fi
else
    print_status "Dry run completed - package built but not released"
fi
