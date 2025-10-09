<#
Creates C:\temp if missing, sets session TEMP/TMP/TMPDIR to it,
runs a small Python tempfile probe using the repo venv python,
prints pip version, attempts to upgrade pip, and attempts a small install
to see if pip's tempfile errors are resolved.
#>
param()

Write-Host "=== probe_and_fix_temp.ps1 starting ==="

$py = 'E:\Projects\Development\python\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    Write-Host "Warning: expected venv python not found at $py" -ForegroundColor Yellow
    Write-Host "Falling back to system 'python' on PATH" -ForegroundColor Yellow
    $py = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    if (-not $py) { Write-Host "No python found on PATH; aborting" -ForegroundColor Red; exit 1 }
}

Write-Host "Using python: $py"

if (-not (Test-Path 'C:\temp')) {
    Write-Host "Creating C:\temp" -ForegroundColor Yellow
    New-Item -Path 'C:\temp' -ItemType Directory | Out-Null
} else {
    Write-Host "C:\temp already exists"
}

$env:TEMP = 'C:\temp'
$env:TMP = 'C:\temp'
$env:TMPDIR = 'C:\temp'
Write-Host "Session TEMP/TMP/TMPDIR = $env:TEMP"

$scriptPath = Join-Path $env:TEMP 'probe_temp.py'
$pythonCode = @'
import tempfile, os, sys
print('gettempdir->', tempfile.gettempdir())
d = tempfile.mkdtemp()
print('mkdtemp->', d)
with open(os.path.join(d, 'x'), 'w') as f:
    f.write('ok')
print('wrote->', os.path.join(d, 'x'))
'@

Set-Content -Path $scriptPath -Value $pythonCode -Encoding ascii

Write-Host "Running tempfile probe script: $scriptPath"
try {
    & $py $scriptPath
} catch {
    Write-Host "Python probe failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "pip --version:";
try { & $py -m pip --version } catch { Write-Host "pip --version failed: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Host "Attempting to upgrade pip (may fail if tempfile still broken)"
try { & $py -m pip install --upgrade pip } catch { Write-Host "pip upgrade failed: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Host "Attempting small package install (colorama) to test pip operations"
try { & $py -m pip install --no-deps --no-build-isolation colorama -v } catch { Write-Host "pip install test failed: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Host "=== probe_and_fix_temp.ps1 complete ==="
