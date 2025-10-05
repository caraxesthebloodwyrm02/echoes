# AI Advisor Environment Validation Script
# This script checks if the development environment is properly configured

param(
    [string]$PythonVersion = "python"
)

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-PythonVersion {
    Write-ColorOutput "Checking Python version..." $Cyan
    try {
        $version = & $PythonVersion --version 2>&1
        Write-ColorOutput "✓ Python found: $version" $Green
        return $true
    }
    catch {
        Write-ColorOutput "✗ Python not found or not accessible" $Red
        return $false
    }
}

function Test-VirtualEnvironment {
    Write-ColorOutput "Checking virtual environment..." $Cyan
    $venvPath = Join-Path $PSScriptRoot "venv"
    $pythonPath = Join-Path $venvPath "Scripts\python.exe"

    if (!(Test-Path $pythonPath)) {
        Write-ColorOutput "✗ Virtual environment not found at $venvPath" $Red
        Write-ColorOutput "   Run: .\setup_environment.ps1" $Yellow
        return $false
    }

    Write-ColorOutput "✓ Virtual environment found" $Green
    return $true
}

function Test-Dependencies {
    Write-ColorOutput "Checking dependencies..." $Cyan
    $pythonPath = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

    $testScript = @"
import sys
import importlib

required_packages = [
    'fastapi',
    'uvicorn',
    'pydantic',
    'httpx',
    'python_jose',
    'passlib',
    'python_dotenv',
    'pytest',
    'black',
    'flake8',
    'mypy'
]

missing_packages = []
for package in required_packages:
    try:
        if package == 'python_jose':
            importlib.import_module('jose')
        else:
            importlib.import_module(package)
        print(f"✓ {package}")
    except ImportError:
        missing_packages.append(package)
        print(f"✗ {package}")

if missing_packages:
    print(f"Missing packages: {', '.join(missing_packages)}")
    sys.exit(1)
else:
    print("All required packages installed")
"@

    & $pythonPath -c $testScript
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Some dependencies are missing" $Red
        Write-ColorOutput "   Run: .\setup_environment.ps1" $Yellow
        return $false
    }

    Write-ColorOutput "✓ All dependencies installed" $Green
    return $true
}

function Test-API {
    Write-ColorOutput "Testing API startup..." $Cyan
    $pythonPath = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

    # Quick syntax check
    & $pythonPath -c "import main_working; print('✓ main_working.py imports successfully')"
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ API has import errors" $Red
        return $false
    }

    Write-ColorOutput "✓ API imports successfully" $Green
    Write-ColorOutput "   To start the API: cd src && python main_working.py" $Yellow
    return $true
}

function Test-Markdown {
    Write-ColorOutput "Checking markdownlint..." $Cyan

    try {
        $version = & npx markdownlint-cli2 --version 2>&1
        Write-ColorOutput "✓ markdownlint found: $version" $Green
        return $true
    }
    catch {
        Write-ColorOutput "⚠ markdownlint not found (optional for development)" $Yellow
        return $true  # Not critical for basic development
    }
}

# Main execution
Write-ColorOutput "🔍 AI Advisor Environment Validation" $Cyan
Write-ColorOutput "====================================" $Cyan

$allChecksPass = $true

$allChecksPass = $allChecksPass -and (Test-PythonVersion)
$allChecksPass = $allChecksPass -and (Test-VirtualEnvironment)
$allChecksPass = $allChecksPass -and (Test-Dependencies)
$allChecksPass = $allChecksPass -and (Test-API)
Test-Markdown  # Optional, don't affect overall result

Write-ColorOutput "`n====================================" $Cyan
if ($allChecksPass) {
    Write-ColorOutput "🎉 All checks passed! Environment is ready." $Green
    Write-ColorOutput "`nNext steps:" $Cyan
    Write-ColorOutput "1. Activate venv: venv\Scripts\activate" $Yellow
    Write-ColorOutput "2. Start API: cd src && python main_working.py" $Yellow
    Write-ColorOutput "3. Open docs: http://localhost:8000/docs" $Yellow
} else {
    Write-ColorOutput "❌ Some checks failed. Please fix the issues above." $Red
    exit 1
}
