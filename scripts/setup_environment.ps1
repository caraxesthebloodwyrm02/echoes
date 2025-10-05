# AI Advisor Environment Setup Script
# This script sets up a Python virtual environment and installs all required dependencies

param(
    [string]$PythonVersion = "python",
    [string]$VenvName = "venv",
    [switch]$Force,
    [switch]$SkipActivation
)

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
$VenvPath = Join-Path $ProjectRoot $VenvName
$PipPath = Join-Path $VenvPath "Scripts\pip.exe"
$PythonPath = Join-Path $VenvPath "Scripts\python.exe"

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
    try {
        $version = & $PythonVersion --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Python found: $version" $Green
            return $true
        }
    }
    catch {
        Write-ColorOutput "✗ Python not found or not accessible" $Red
        return $false
    }
    return $false
}

function Remove-OldVenv {
    if (Test-Path $VenvPath) {
        Write-ColorOutput "Removing existing virtual environment..." $Yellow
        Remove-Item -Recurse -Force $VenvPath
    }
}

function Create-VirtualEnvironment {
    Write-ColorOutput "Creating virtual environment..." $Cyan
    & $PythonVersion -m venv $VenvName
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Failed to create virtual environment" $Red
        exit 1
    }
    Write-ColorOutput "✓ Virtual environment created successfully" $Green
}

function Upgrade-Pip {
    Write-ColorOutput "Upgrading pip..." $Cyan
    & $PipPath install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "⚠ Warning: Failed to upgrade pip, continuing..." $Yellow
    } else {
        Write-ColorOutput "✓ Pip upgraded successfully" $Green
    }
}

function Install-Requirements {
    if (!(Test-Path $RequirementsFile)) {
        Write-ColorOutput "✗ Requirements file not found: $RequirementsFile" $Red
        exit 1
    }

    Write-ColorOutput "Installing requirements from $RequirementsFile..." $Cyan
    & $PipPath install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Failed to install requirements" $Red
        exit 1
    }
    Write-ColorOutput "✓ All requirements installed successfully" $Green
}

function Test-Installation {
    Write-ColorOutput "Testing installation..." $Cyan

    # Test FastAPI import
    $testScript = @"
try:
    import fastapi
    import uvicorn
    print("✓ Core dependencies imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
"@

    $result = & $PythonPath -c $testScript
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "✗ Installation test failed" $Red
        exit 1
    }
    Write-ColorOutput $result $Green
}

function Show-ActivationInstructions {
    Write-ColorOutput "`n🎉 Environment setup complete!" $Green
    Write-ColorOutput "`nTo activate the virtual environment, run:" $Cyan
    Write-ColorOutput "    $VenvName\Scripts\activate" $Yellow
    Write-ColorOutput "`nTo run the AI Advisor API:" $Cyan
    Write-ColorOutput "    cd src" $Yellow
    Write-ColorOutput "    python main.py" $Yellow
    Write-ColorOutput "`nTo view the API documentation:" $Cyan
    Write-ColorOutput "    http://localhost:8000/docs" $Yellow
}

# Main execution
Write-ColorOutput "🚀 AI Advisor Environment Setup" $Cyan
Write-ColorOutput "=================================" $Cyan

# Change to project root
Set-Location $ProjectRoot

# Check Python availability
if (!(Test-PythonVersion)) {
    Write-ColorOutput "`nPlease ensure Python 3.10+ is installed and available in PATH." $Yellow
    Write-ColorOutput "Alternatively, specify the Python executable with -PythonVersion parameter." $Yellow
    exit 1
}

# Handle existing venv
if ((Test-Path $VenvPath) -and !$Force) {
    Write-ColorOutput "`nVirtual environment already exists at $VenvPath" $Yellow
    $response = Read-Host "Do you want to recreate it? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-OldVenv
    } else {
        Write-ColorOutput "Setup cancelled." $Yellow
        exit 0
    }
} elseif ($Force) {
    Remove-OldVenv
}

# Create and setup environment
Create-VirtualEnvironment
Upgrade-Pip
Install-Requirements
Test-Installation

if (!$SkipActivation) {
    Show-ActivationInstructions
} else {
    Write-ColorOutput "`n🎉 Environment setup complete!" $Green
}
