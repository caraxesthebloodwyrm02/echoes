#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Weekly Security Check Script for Development Environment
.DESCRIPTION
    Performs comprehensive security checks including Docker vulnerabilities,
    container security, file permissions, security logs, and dependency checks.
.PARAMETER OutputPath
    Path to save the security report (default: ./security-report-$(Get-Date -Format 'yyyy-MM-dd').md)
.PARAMETER Verbose
    Enable verbose output
#>

param(
    [string]$OutputPath = $null,
    [switch]$Verbose
)

# Set default output path if not provided
if (-not $OutputPath) {
    $OutputPath = Join-Path $PSScriptRoot "..\security-report-$(Get-Date -Format 'yyyy-MM-dd').md"
}

# Ensure we're in the project root
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

# Script configuration
$ScriptName = "Weekly Security Check"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$LogFile = Join-Path $PSScriptRoot "..\logs\security-check.log"

# Create logs directory if it doesn't exist
$LogDir = Split-Path $LogFile -Parent
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Initialize report
$Report = @()
$Issues = @()
$Warnings = @()

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogMessage = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Write-Verbose $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Add-ReportSection {
    param([string]$Title, [string]$Content)
    $Report += "## $Title`n`n$Content`n"
}

function Add-Issue {
    param([string]$Issue, [string]$Severity = "MEDIUM")
    $Issues += @{Issue = $Issue; Severity = $Severity}
    $Report += "❌ **$Severity**: $Issue`n"
    Write-Log "ISSUE ($Severity): $Issue" "WARN"
}

function Add-Warning {
    param([string]$Warning)
    $Warnings += $Warning
    $Report += "⚠️ **WARNING**: $Warning`n"
    Write-Log "WARNING: $Warning" "WARN"
}

function Add-Success {
    param([string]$Message)
    $Report += "✅ $Message`n"
    Write-Log $Message "INFO"
}

Write-Log "Starting $ScriptName at $Timestamp"

# Header
$Report += "# $ScriptName - $Timestamp`n`n"
# 1. Docker Security Checks
Add-ReportSection "Docker Security Status" "Checking Docker images, containers, and security settings..."
try {
    # Check if Docker is running
    docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Add-Success "Docker daemon is running"

        # Check for vulnerable images
        $vulnerableImages = docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}" | Select-String -Pattern "weeks ago|months ago|years ago"
        if ($vulnerableImages) {
{{ ... }}
            Add-Warning "Found potentially outdated images. Consider updating: $($vulnerableImages.Line)"
        } else {
            Add-Success "No obviously outdated images found"
        }

        # Check running containers
        $runningContainers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        if ($runningContainers.Count -gt 1) {
            $Report += "Running containers:`n```$runningContainers`n```n"
        }

        # Check container security
        $containers = docker ps -q
        if ($containers) {
            foreach ($container in $containers) {
                $containerInfo = docker inspect $container | ConvertFrom-Json
                $privileged = $containerInfo.HostConfig.Privileged
                if ($privileged) {
                    Add-Issue "Container $($containerInfo.Name) is running in privileged mode" "HIGH"
                }
                $readonly = $containerInfo.HostConfig.ReadonlyRootfs
                if (-not $readonly) {
                    Add-Warning "Container $($containerInfo.Name) does not have read-only root filesystem"
                }
            }
        }

    } else {
        Add-Issue "Docker daemon is not running" "HIGH"
    }
} catch {
    Add-Issue "Failed to check Docker status: $($_.Exception.Message)" "MEDIUM"
}

# 2. File System Security Checks
Add-ReportSection "File System Security" "Checking file permissions and security settings..."

try {
    # Check .env file permissions
    if (Test-Path ".env") {
        $envAcl = Get-Acl ".env"
        $envPermissions = $envAcl.Access | Where-Object { $_.FileSystemRights -ne "FullControl" -and $_.IdentityReference -ne "BUILTIN\Administrators" }
        if ($envPermissions) {
            Add-Issue ".env file has overly permissive permissions" "HIGH"
        } else {
            Add-Success ".env file has secure permissions"
        }
    }

    # Check for world-writable files in sensitive directories
    $worldWritable = Get-ChildItem -Path "." -Recurse -File -ErrorAction SilentlyContinue | 
                     Where-Object { $_.Attributes -band [System.IO.FileAttributes]::Normal } |
                     Get-Acl | Where-Object { $_.Access | Where-Object { $_.FileSystemRights -eq "FullControl" -and $_.IdentityReference -eq "Everyone" } }
    
    if ($worldWritable) {
        Add-Warning "Found $($worldWritable.Count) world-writable files"
    } else {
        Add-Success "No world-writable files found"
    }

} catch {
    Add-Issue "Failed to check file system security: $($_.Exception.Message)" "MEDIUM"
}

# 3. Security Logs Check
Add-ReportSection "Security Logs" "Checking recent security events and logs..."

try {
    # Check for recent failed login attempts (if available)
    if (Test-Path "logs\security.log") {
        $recentFailures = Get-Content "logs\security.log" -Tail 10 | Select-String -Pattern "failed|error|unauthorized|denied"
        if ($recentFailures) {
            Add-Warning "Found recent security events in logs: $($recentFailures.Count) entries"
        } else {
            Add-Success "No recent security events found in logs"
        }
    }

    # Check auth.log if available (Linux systems)
    if (Test-Path "/var/log/auth.log") {
        $recentAuthFailures = Get-Content "/var/log/auth.log" -Tail 20 2>$null | Select-String -Pattern "Failed|invalid|authentication failure"
        if ($recentAuthFailures) {
            Add-Issue "Found authentication failures in system logs" "MEDIUM"
        }
    }

} catch {
    Add-Issue "Failed to check security logs: $($_.Exception.Message)" "LOW"
}

# 4. Network Security Check
Add-ReportSection "Network Security" "Checking network configurations and open ports..."

try {
    # Check for open ports (basic check)
    $openPorts = netstat -an 2>$null | Select-String -Pattern "LISTEN"
    if ($openPorts) {
        $Report += "Open listening ports:`n```$($openPorts.Line)`n```n"
    }

    # Check firewall status (Windows)
    $firewallStatus = Get-NetFirewallProfile 2>$null
    if ($firewallStatus) {
        foreach ($firewallProfile in $firewallStatus) {
            if ($firewallProfile.Enabled) {
                Add-Success "Firewall enabled for $($firewallProfile.Name) profile"
            } else {
                Add-Issue "Firewall disabled for $($firewallProfile.Name) profile" "HIGH"
            }
        }
    }

} catch {
    Add-Issue "Failed to check network security: $($_.Exception.Message)" "MEDIUM"
}

# 5. Dependency Security Check
Add-ReportSection "Dependency Security" "Checking Python packages and other dependencies..."

try {
    if (Test-Path "requirements.txt") {
        Add-Success "requirements.txt found"
        
        # Check for outdated packages (if pip-tools or similar is available)
        try {
            $outdated = pip list --outdated 2>$null
            if ($outdated -and $outdated.Count -gt 1) {
                Add-Warning "Found $($outdated.Count - 1) outdated Python packages"
            } else {
                Add-Success "All Python packages are up to date"
            }
        } catch {
            Add-Warning "Could not check for outdated Python packages"
        }
    }

    if (Test-Path "package.json") {
        Add-Success "package.json found"
        # Could add npm audit check here if Node.js dependencies exist
    }

} catch {
    Add-Issue "Failed to check dependencies: $($_.Exception.Message)" "MEDIUM"
}

# 6. Backup Check
Add-ReportSection "Backup Status" "Checking backup configurations and recent backups..."

try {
    # Check for backup directory
    if (Test-Path "backups") {
        $backupFiles = Get-ChildItem "backups" -File | Sort-Object LastWriteTime -Descending
        if ($backupFiles.Count -gt 0) {
            $latestBackup = $backupFiles[0]
            $backupAge = (Get-Date) - $latestBackup.LastWriteTime
            if ($backupAge.Days -gt 7) {
                Add-Warning "Latest backup is $($backupAge.Days) days old"
            } else {
                Add-Success "Latest backup is recent ($($backupAge.Days) days old)"
            }
        } else {
            Add-Issue "No backup files found" "MEDIUM"
        }
    } else {
        Add-Warning "No backups directory found"
    }

} catch {
    Add-Issue "Failed to check backup status: $($_.Exception.Message)" "LOW"
}

# Summary
$Report += "## Summary`n`n"

if ($Issues.Count -eq 0) {
    Add-Success "No security issues found"
} else {
    $Report += "**Issues Found:** $($Issues.Count)`n"
    $highIssues = $Issues | Where-Object { $_.Severity -eq "HIGH" }
    if ($highIssues) {
        $Report += "**High Priority Issues:** $($highIssues.Count)`n"
    }
}

if ($Warnings.Count -gt 0) {
    $Report += "**Warnings:** $($Warnings.Count)`n"
}

$Report += "**Recommendations:**`n"
$Report += "- Review and address any HIGH severity issues immediately`n"
$Report += "- Address MEDIUM severity issues within the next week`n"
$Report += "- Monitor LOW severity issues for patterns`n"
$Report += "- Run this check weekly to maintain security posture`n"

# Save report
$Report | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Log "Security report saved to: $OutputPath"

# Output summary to console
Write-Host "`n=== SECURITY CHECK SUMMARY ===" -ForegroundColor Cyan
Write-Host "Report saved to: $OutputPath" -ForegroundColor Green
Write-Host "Issues found: $($Issues.Count)" -ForegroundColor $(if ($Issues.Count -gt 0) { "Red" } else { "Green" })
Write-Host "Warnings: $($Warnings.Count)" -ForegroundColor $(if ($Warnings.Count -gt 0) { "Yellow" } else { "Green" })

if ($Issues.Count -gt 0) {
    Write-Host "`nHIGH PRIORITY ISSUES:" -ForegroundColor Red
    $Issues | Where-Object { $_.Severity -eq "HIGH" } | ForEach-Object {
        Write-Host "  - $($_.Issue)" -ForegroundColor Red
    }
}

Write-Host "`nWeekly security check completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
EOF




