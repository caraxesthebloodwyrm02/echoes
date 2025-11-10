# Fix common code quality issues
param(
    [switch]$FixAll,
    [switch]$LintOnly,
    [switch]$TestOnly,
    [string]$PythonVersion = "3.12"
)

function Write-Header {
    param($Message)
    Write-Host "`n=== $Message ===`n" -ForegroundColor Cyan
}

function Initialize-Environment {
    Write-Header "Setting up Python environment"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -e ".[dev]"
}

function Run-Linter {
    Write-Header "Running linters"
    
    # Auto-fix what we can
    ruff check . --fix --unsafe-fixes
    black .
    
    # Show remaining issues
    ruff check . --show-source
}

function Run-Tests {
    param($WithCoverage = $true)
    
    Write-Header "Running tests"
    $coverageArgs = @("--cov=app", "--cov=core_modules", "--cov=api", "--cov-report=term-missing")
    if (-not $WithCoverage) { $coverageArgs = @() }
    
    pytest tests/ -v --tb=short --maxfail=5 --timeout=300 @coverageArgs
}

function Main {
    # Set error action preference
    $ErrorActionPreference = "Stop"
    
    try {
        # Run all checks by default
        if (-not ($LintOnly -or $TestOnly)) { $FixAll = $true }
        
        if ($FixAll -or $LintOnly) {
            Run-Linter
        }
        
        if ($FixAll -or $TestOnly) {
            Run-Tests -WithCoverage:(-not $TestOnly)
        }
        
        Write-Host "`n✅ All checks completed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "`n❌ Error: $_" -ForegroundColor Red
        exit 1
    }
}

# Run the main function
Main
