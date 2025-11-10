param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("lint", "test", "policy", "audit", "security", "clean", "install-dev", "check-versions", "format", "docs", "ci", "dev-setup", "quick", "sec-check", "policy-check")]
    [string]$Task = "help"
)

function Show-Help {
    Write-Host "Available tasks:" -ForegroundColor Green
    Write-Host "  lint        - Run code linting checks"
    Write-Host "  test        - Run unit tests with coverage"
    Write-Host "  policy      - Verify egress policy configuration"
    Write-Host "  audit       - Run security audits (pip-audit, safety, SBOM)"
    Write-Host "  security    - Run Bandit security analysis"
    Write-Host "  clean       - Clean build artifacts and cache"
    Write-Host "  install-dev - Install development dependencies"
    Write-Host "  check-versions - Verify security tooling versions"
    Write-Host "  format      - Format code with black and isort"
    Write-Host "  docs        - Show documentation files"
    Write-Host "  ci          - Run all CI checks"
    Write-Host "  dev-setup   - Setup development environment"
    Write-Host "  quick       - Quick lint + test"
    Write-Host "  sec-check   - Security audit + analysis"
    Write-Host "  policy-check - Policy + version check"
}

function Invoke-Lint {
    Write-Host "Running linting checks..." -ForegroundColor Yellow
    black --check .
    isort --check-only .
    ruff check .
    mypy core_modules/
}

function Invoke-Test {
    Write-Host "Running tests with coverage..." -ForegroundColor Yellow
    pytest tests/ -v --cov=core_modules --cov-report=xml --cov-report=html --cov-report=term-missing
}

function Invoke-Policy {
    Write-Host "Verifying egress policy..." -ForegroundColor Yellow
    python -m core_modules.network.policy --verify
    python -m core_modules.network.policy --print
}

function Invoke-Audit {
    Write-Host "Running security audits..." -ForegroundColor Yellow
    pip-audit --requirement requirements.txt
    safety check --full-report -r requirements.txt
    cyclonedx-py requirements -r requirements.txt -o sbom.xml
}

function Invoke-Security {
    Write-Host "Running Bandit security analysis..." -ForegroundColor Yellow
    bandit -r . -c bandit.yaml -f json -o bandit-report.json
    bandit -r . -c bandit.yaml -f txt
}

function Invoke-Clean {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    $dirs = @(".pytest_cache", "__pycache__", ".coverage", "htmlcov", ".mypy_cache", "dist", "build")
    foreach ($dir in $dirs) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Host "Cleaned $dir"
        }
    }
    
    # Clean .pyc and .pyo files
    Get-ChildItem -Recurse -Include "*.pyc", "*.pyo" | Remove-Item -Force
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

function Invoke-InstallDev {
    Write-Host "Installing development dependencies..." -ForegroundColor Yellow
    pip install -e .
    pip install -r requirements.txt
    pip install -r requirements-security.txt
}

function Invoke-CheckVersions {
    Write-Host "Verifying security tooling versions..." -ForegroundColor Yellow
    python tools/verify_versions.py
}

function Invoke-Format {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    black .
    isort .
}

function Show-Docs {
    Write-Host "Documentation files:" -ForegroundColor Green
    Get-ChildItem -Path "docs" -Filter "*.md" -Recurse | Sort-Object Name | ForEach-Object { Write-Host "  $($_.FullName)" }
}

function Invoke-CI {
    Write-Host "Running all CI checks..." -ForegroundColor Yellow
    Invoke-Lint
    Invoke-Test
    Invoke-Policy
    Invoke-Audit
    Invoke-Security
    Invoke-CheckVersions
    Write-Host "All CI checks completed successfully!" -ForegroundColor Green
}

function Invoke-DevSetup {
    Write-Host "Setting up development environment..." -ForegroundColor Yellow
    Invoke-InstallDev
    Invoke-Format
    Invoke-Test
    Write-Host "Development environment setup complete!" -ForegroundColor Green
}

function Invoke-Quick {
    Write-Host "Running quick checks..." -ForegroundColor Yellow
    Invoke-Lint
    Invoke-Test
    Write-Host "Quick checks completed!" -ForegroundColor Green
}

function Invoke-SecCheck {
    Write-Host "Running security checks..." -ForegroundColor Yellow
    Invoke-Audit
    Invoke-Security
    Invoke-CheckVersions
    Write-Host "Security checks completed!" -ForegroundColor Green
}

function Invoke-PolicyCheck {
    Write-Host "Running policy checks..." -ForegroundColor Yellow
    Invoke-Policy
    Invoke-CheckVersions
    Write-Host "Policy checks completed!" -ForegroundColor Green
}

# Main execution
switch ($Task) {
    "help" { Show-Help }
    "lint" { Invoke-Lint }
    "test" { Invoke-Test }
    "policy" { Invoke-Policy }
    "audit" { Invoke-Audit }
    "security" { Invoke-Security }
    "clean" { Invoke-Clean }
    "install-dev" { Invoke-InstallDev }
    "check-versions" { Invoke-CheckVersions }
    "format" { Invoke-Format }
    "docs" { Show-Docs }
    "ci" { Invoke-CI }
    "dev-setup" { Invoke-DevSetup }
    "quick" { Invoke-Quick }
    "sec-check" { Invoke-SecCheck }
    "policy-check" { Invoke-PolicyCheck }
    default { 
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
