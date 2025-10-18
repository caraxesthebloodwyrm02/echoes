<#
Admin helper: relaunches elevated and attempts to fix Python/pip tempfile failures.
It will:
 - add the repo venv python executable to Controlled Folder Access allowed apps (if Defender supports it)
 - set system TEMP/TMP to C:\temp
 - grant current user Full Control on C:\temp
 - run the `tools/temp_probe.py` and a small pip install test

This script will prompt for UAC when relaunching elevated.
Run only if you understand these system-level changes.
#>

function Is-Administrator {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($current)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$scriptPath = $MyInvocation.MyCommand.Path
Write-Host "=== admin_fix_temp.ps1 starting ==="

if (-not (Is-Administrator)) {
    Write-Host "Not running as Administrator. Relaunching with elevation (UAC prompt expected)..." -ForegroundColor Yellow
    Start-Process -FilePath pwsh -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    exit
}

Write-Host "Running as Administrator." -ForegroundColor Green

# Ensure C:\temp
if (-not (Test-Path 'C:\temp')) {
    Write-Host "Creating C:\temp" -ForegroundColor Yellow
    New-Item -Path 'C:\temp' -ItemType Directory | Out-Null
} else { Write-Host "C:\temp already exists" }

# Grant current user Full Control on C:\temp
try {
    $user = "$env:USERDOMAIN\\$env:USERNAME"
    Write-Host "Granting FullControl on C:\temp to $user"
    $aclArg = $user + ':(OI)(CI)F'
    & icacls C:\temp /grant $aclArg /C | Out-Null
    Write-Host "ACL update attempted"
} catch {
    Write-Host "ACL update failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Attempt to add python exe to Controlled Folder Access allowed applications (if available)
$py = 'E:\Projects\Development\python\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = (Get-Command python -ErrorAction SilentlyContinue)?.Source }
if ($py) {
    try {
        Write-Host "Attempting to add $py to Controlled Folder Access allowed apps (requires Defender/Powershell support)"
        Add-MpPreference -ControlledFolderAccessAllowedApplications $py -ErrorAction Stop
        Write-Host "Added to Controlled Folder Access allowed apps (if supported)" -ForegroundColor Green
    } catch {
        Write-Host "Could not add to Controlled Folder Access (command unavailable or failed): $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "No python executable found to add to Controlled Folder Access" -ForegroundColor Yellow
}

# Set machine TEMP/TMP to C:\temp
try {
    Write-Host "Setting system TEMP/TMP to C:\temp"
    [Environment]::SetEnvironmentVariable('TEMP','C:\temp','Machine')
    [Environment]::SetEnvironmentVariable('TMP','C:\temp','Machine')
    Write-Host "System TEMP/TMP set. You may need to log off/log on for all processes to see the change." -ForegroundColor Yellow
} catch {
    Write-Host "Failed to set system TEMP/TMP: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Update current session env too
$env:TEMP = 'C:\temp'; $env:TMP = 'C:\temp'; $env:TMPDIR = 'C:\temp'

Write-Host "Session TEMP/TMP/TMPDIR = $env:TEMP"

Write-Host "Running temp probe and pip checks"
try { & 'E:\Projects\Development\python\.venv\Scripts\python.exe' 'tools\temp_probe.py' } catch { Write-Host "Probe run failed: $($_.Exception.Message)" -ForegroundColor Yellow }
try { & 'E:\Projects\Development\python\.venv\Scripts\python.exe' -m pip --version } catch { Write-Host "pip --version failed: $($_.Exception.Message)" -ForegroundColor Yellow }
try { & 'E:\Projects\Development\python\.venv\Scripts\python.exe' -m pip install --upgrade pip } catch { Write-Host "pip upgrade failed: $($_.Exception.Message)" -ForegroundColor Yellow }
try { & 'E:\Projects\Development\python\.venv\Scripts\python.exe' -m pip install --no-deps --no-build-isolation colorama -v } catch { Write-Host "pip install test failed: $($_.Exception.Message)" -ForegroundColor Yellow }

Write-Host "=== admin_fix_temp.ps1 complete ==="
