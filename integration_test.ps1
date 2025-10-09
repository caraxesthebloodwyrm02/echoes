<#
Deterministic integration test for the FastAPI /transform endpoint.
Creates/uses python/.venv, installs requirements, starts the uvicorn server, posts {"text":"abc"}
and expects the deterministic local fallback: "[local-echo] cba" when OPENAI_API_KEY is unset.
#>
param(
    [int]$Port = 8000
)

Write-Host "=== integration_test.ps1 starting ==="

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyDir = Join-Path $root 'python'
$venv = Join-Path $pyDir '.venv'

if (-not (Test-Path $pyDir)) {
    Write-Host "Creating python folder at $pyDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $pyDir | Out-Null
}

# Find a usable python executable
$systemPython = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if (-not $systemPython) {
    Write-Host "No 'python' on PATH. Please install Python or set PATH accordingly." -ForegroundColor Red
    exit 4
}

if (-not (Test-Path $venv)) {
    Write-Host "Creating venv at $venv using $systemPython"
    & $systemPython -m venv $venv
}

$pythonExe = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
    Write-Host "Virtualenv python not found at $pythonExe, falling back to system python: $systemPython" -ForegroundColor Yellow
    $pythonExe = $systemPython
}

Write-Host "Installing requirements (if any) with $pythonExe"
$req = Join-Path $pyDir 'requirements.txt'
# Ensure a repo-local temp directory for pip/tempfile to avoid system temp issues
$pipTempDir = Join-Path $root 'pip_temp'
if (-not (Test-Path $pipTempDir)) {
    Write-Host "Creating local pip temp dir at $pipTempDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $pipTempDir | Out-Null
}
$env:TEMP = $pipTempDir
$env:TMP = $pipTempDir
Write-Host "Using TEMP/TMP = $pipTempDir for pip operations"
# If we're using the virtualenv python, don't use --user (not supported)
$pipUserArg = "--user"
if ($pythonExe -like "*\python\.venv*" -or $pythonExe -like "*\\python\\.venv*" -or (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
    $pipUserArg = ""
}
if (Test-Path $req) {
    # Try a small pip operation to detect whether pip/tempfile is functional in this environment.
    $pipCheckOk = $true
    try {
        Write-Host "Checking pip functionality (no-op)" -ForegroundColor Cyan
        & $pythonExe -m pip --version > $null
    } catch {
        Write-Host "pip check failed: $($_.Exception.Message)" -ForegroundColor Yellow
        $pipCheckOk = $false
    }

    if ($pipCheckOk) {
        Write-Host "Installing/Upgrading pip and requirements"
        if ($pipUserArg -ne "") { & $pythonExe -m pip install --upgrade pip $pipUserArg } else { & $pythonExe -m pip install --upgrade pip }
        if ($pipUserArg -ne "") { & $pythonExe -m pip install -r $req $pipUserArg } else { & $pythonExe -m pip install -r $req }
    } else {
        Write-Host "Skipping pip install due to pip/tempfile failures; relying on existing venv packages." -ForegroundColor Yellow
    }
} else {
    Write-Host "No requirements.txt found at $req" -ForegroundColor Yellow
}

Write-Host "Starting uvicorn in background using $pythonExe"
$env:OPENAI_API_KEY = ''
$args = @('-m','uvicorn','service:app','--host','127.0.0.1','--port',$Port)
# Start uvicorn with working directory set to the python folder so 'service' module is importable
$proc = Start-Process -FilePath $pythonExe -ArgumentList $args -WorkingDirectory $pyDir -NoNewWindow -PassThru

# Poll for readiness
$uri = "http://127.0.0.1:$Port/transform"
$ready = $false
for ($i=0; $i -lt 15; $i++) {
    try {
            Start-Sleep -Seconds 1
            $r = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$Port/health" -ErrorAction Stop
        $ready = $true
        break
    } catch { }
}

if (-not $ready) {
    Write-Host "Integration test: ERROR - server did not start within timeout" -ForegroundColor Red
    if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
    exit 5
}

try {
    $body = @{ text = 'abc' } | ConvertTo-Json
    Write-Host "POST $uri -> $body"
    $resp = Invoke-RestMethod -Method Post -Uri $uri -ContentType 'application/json' -Body $body -ErrorAction Stop
    Write-Host "Response: $($resp | ConvertTo-Json -Depth 5)"
    if ($resp.result -eq '[local-echo] cba') {
        Write-Host 'Integration test: PASS' -ForegroundColor Green
    } else {
        Write-Host 'Integration test: FAIL (unexpected response)' -ForegroundColor Red
        exit 2
    }
} catch {
    Write-Host "Integration test: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    exit 3
} finally {
    if ($proc -and -not $proc.HasExited) {
        Write-Host "Stopping uvicorn (PID $($proc.Id))"
        Stop-Process -Id $proc.Id -Force
    }
}

Write-Host "=== Integration test complete ==="
