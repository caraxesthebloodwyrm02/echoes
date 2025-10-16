# Test Maintenance System
# Quick validation that the maintenance scripts are working

Write-Host "Testing Echoes Project Maintenance System..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

$ProjectRoot = $PSScriptRoot  # Use current script directory
$MaintenanceScript = Join-Path $ProjectRoot "scheduled_maintenance.ps1"
$SetupScript = Join-Path $ProjectRoot "setup_maintenance_task.ps1"

# Test 1: Check if scripts exist
Write-Host "Test 1: Checking script files..." -ForegroundColor Cyan
$ScriptsExist = $true
if (!(Test-Path $MaintenanceScript)) {
    Write-Host "❌ Maintenance script not found: $MaintenanceScript" -ForegroundColor Red
    $ScriptsExist = $false
} else {
    Write-Host "✅ Maintenance script found" -ForegroundColor Green
}

if (!(Test-Path $SetupScript)) {
    Write-Host "❌ Setup script not found: $SetupScript" -ForegroundColor Red
    $ScriptsExist = $false
} else {
    Write-Host "✅ Setup script found" -ForegroundColor Green
}

# Test 2: Check data directories
Write-Host "`nTest 2: Checking data directories..." -ForegroundColor Cyan
$DataDir = Join-Path $ProjectRoot "data"
$ContextDir = Join-Path $DataDir "context"
$CacheDir = Join-Path $DataDir "cache"

if (Test-Path $DataDir) {
    Write-Host "✅ Data directory exists" -ForegroundColor Green

    if (Test-Path $ContextDir) {
        $ContextFiles = (Get-ChildItem $ContextDir -File -ErrorAction SilentlyContinue).Count
        Write-Host "✅ Context directory exists ($ContextFiles files)" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ Context directory doesn't exist yet (will be created as needed)" -ForegroundColor Yellow
    }

    if (Test-Path $CacheDir) {
        $CacheFiles = (Get-ChildItem $CacheDir -File -ErrorAction SilentlyContinue).Count
        Write-Host "✅ Cache directory exists ($CacheFiles files)" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ Cache directory doesn't exist yet (will be created as needed)" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ️ Data directory doesn't exist yet" -ForegroundColor Yellow
}

# Test 3: Check memory files
Write-Host "`nTest 3: Checking memory files..." -ForegroundColor Cyan
$MemoryFiles = @(
    (Join-Path $DataDir "memory.json"),
    (Join-Path $DataDir "organizing_memory.json")
)

foreach ($File in $MemoryFiles) {
    if (Test-Path $File) {
        $Size = (Get-Item $File).Length
        $SizeMB = [math]::Round($Size / 1MB, 2)
        Write-Host "✅ $($File | Split-Path -Leaf) exists ($SizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ $($File | Split-Path -Leaf) doesn't exist yet" -ForegroundColor Yellow
    }
}

# Test 4: Validate script syntax
Write-Host "`nTest 4: Validating script syntax..." -ForegroundColor Cyan
try {
    $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $MaintenanceScript -Raw), [ref]$null)
    Write-Host "✅ Maintenance script syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Maintenance script syntax error: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $SetupScript -Raw), [ref]$null)
    Write-Host "✅ Setup script syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Setup script syntax error: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Yellow
Write-Host "Maintenance System Test Complete" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "To set up scheduled maintenance:" -ForegroundColor White
Write-Host "  1. Run: .\setup_maintenance.bat" -ForegroundColor Cyan
Write-Host "  2. Choose option 1 (daily) or 2 (weekly)" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "To run maintenance manually:" -ForegroundColor White
Write-Host "  Dry run: .\scheduled_maintenance.ps1 -DryRun -Verbose" -ForegroundColor Cyan
Write-Host "  Full run: .\scheduled_maintenance.ps1 -Verbose" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "For more information, see MAINTENANCE_README.md" -ForegroundColor Magenta
