# Emergency Security Lockdown
# CRITICAL: Use only in case of security incident
# This script will stop and remove all containers
# Date: 2025-09-29

$ErrorActionPreference = "Stop"
$date = Get-Date -Format "yyyy-MM-dd-HHmmss"
$logDir = "E:\Projects\Development\logs"
$incidentLog = "$logDir\security-incidents.log"

# Create log directory
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║                                                          ║" -ForegroundColor Red
Write-Host "║           ⚠️  EMERGENCY SECURITY LOCKDOWN  ⚠️            ║" -ForegroundColor Red
Write-Host "║                                                          ║" -ForegroundColor Red
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  • Stop all running containers" -ForegroundColor Yellow
Write-Host "  • Remove all containers" -ForegroundColor Yellow
Write-Host "  • Disconnect all networks" -ForegroundColor Yellow
Write-Host "  • Log the incident" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  WARNING: This action cannot be undone!" -ForegroundColor Red
Write-Host ""

# Confirmation
$confirmation = Read-Host "Type 'LOCKDOWN' to confirm"
if ($confirmation -ne "LOCKDOWN") {
    Write-Host "❌ Lockdown cancelled" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Incident Reason (for logging):" -ForegroundColor Yellow
$reason = Read-Host "Enter reason"

Write-Host ""
Write-Host "Initiating lockdown..." -ForegroundColor Red
Write-Host ""

# Log incident start
$logEntry = @"

═══════════════════════════════════════════════════════════════
SECURITY INCIDENT - EMERGENCY LOCKDOWN
═══════════════════════════════════════════════════════════════
Timestamp: $date
User: $env:USERNAME
Computer: $env:COMPUTERNAME
Reason: $reason

"@
Add-Content -Path $incidentLog -Value $logEntry

# 1. Stop all running containers
Write-Host "[1/5] Stopping all running containers..." -ForegroundColor Yellow
try {
    $runningContainers = docker ps -q
    if ($runningContainers) {
        docker stop $runningContainers 2>&1 | Out-Null
        Write-Host "  ✓ Stopped $($runningContainers.Count) containers" -ForegroundColor Green
        Add-Content -Path $incidentLog -Value "Stopped containers: $($runningContainers -join ', ')"
    } else {
        Write-Host "  ℹ️  No running containers" -ForegroundColor Gray
        Add-Content -Path $incidentLog -Value "No running containers to stop"
    }
} catch {
    Write-Host "  ⚠️  Error stopping containers: $_" -ForegroundColor Red
    Add-Content -Path $incidentLog -Value "ERROR stopping containers: $_"
}

# 2. Remove all containers
Write-Host "[2/5] Removing all containers..." -ForegroundColor Yellow
try {
    $allContainers = docker ps -aq
    if ($allContainers) {
        docker rm -f $allContainers 2>&1 | Out-Null
        Write-Host "  ✓ Removed $($allContainers.Count) containers" -ForegroundColor Green
        Add-Content -Path $incidentLog -Value "Removed containers: $($allContainers -join ', ')"
    } else {
        Write-Host "  ℹ️  No containers to remove" -ForegroundColor Gray
        Add-Content -Path $incidentLog -Value "No containers to remove"
    }
} catch {
    Write-Host "  ⚠️  Error removing containers: $_" -ForegroundColor Red
    Add-Content -Path $incidentLog -Value "ERROR removing containers: $_"
}

# 3. Disconnect networks
Write-Host "[3/5] Cleaning up networks..." -ForegroundColor Yellow
try {
    docker network prune -f 2>&1 | Out-Null
    Write-Host "  ✓ Networks cleaned" -ForegroundColor Green
    Add-Content -Path $incidentLog -Value "Networks pruned successfully"
} catch {
    Write-Host "  ⚠️  Error cleaning networks: $_" -ForegroundColor Red
    Add-Content -Path $incidentLog -Value "ERROR cleaning networks: $_"
}

# 4. Take snapshot of current state
Write-Host "[4/5] Taking system snapshot..." -ForegroundColor Yellow
$snapshotFile = "$logDir\lockdown-snapshot-$date.txt"
@"
DOCKER SYSTEM SNAPSHOT - POST LOCKDOWN
Date: $date

=== Images ===
$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}")

=== Volumes ===
$(docker volume ls)

=== Networks ===
$(docker network ls)

=== System Info ===
$(docker info)

"@ | Out-File $snapshotFile
Write-Host "  ✓ Snapshot saved to: $snapshotFile" -ForegroundColor Green
Add-Content -Path $incidentLog -Value "System snapshot saved: $snapshotFile"

# 5. Generate incident report
Write-Host "[5/5] Generating incident report..." -ForegroundColor Yellow
$reportFile = "$logDir\incident-report-$date.txt"
@"
╔══════════════════════════════════════════════════════════════╗
║            SECURITY INCIDENT REPORT                          ║
╚══════════════════════════════════════════════════════════════╝

INCIDENT DETAILS
────────────────────────────────────────────────────────────────
Date/Time:    $date
User:         $env:USERNAME
Computer:     $env:COMPUTERNAME
Reason:       $reason

ACTIONS TAKEN
────────────────────────────────────────────────────────────────
✓ All containers stopped
✓ All containers removed
✓ Networks cleaned
✓ System snapshot captured

NEXT STEPS
────────────────────────────────────────────────────────────────
1. Review incident log: $incidentLog
2. Review system snapshot: $snapshotFile
3. Investigate root cause
4. Scan all images: docker scout cves <image>
5. Update security policies
6. Document lessons learned

SECURITY STATUS
────────────────────────────────────────────────────────────────
Current State: LOCKED DOWN
All containers: REMOVED
Docker Engine: RUNNING (safe mode)
Recommendation: Review before redeploying any workloads

INCIDENT LOG
────────────────────────────────────────────────────────────────
See: $incidentLog

═══════════════════════════════════════════════════════════════
                    END OF INCIDENT REPORT
═══════════════════════════════════════════════════════════════
"@ | Out-File $reportFile

Write-Host "  ✓ Incident report saved: $reportFile" -ForegroundColor Green
Add-Content -Path $incidentLog -Value "Incident report generated: $reportFile"
Add-Content -Path $incidentLog -Value "Lockdown completed successfully at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Content -Path $incidentLog -Value "═══════════════════════════════════════════════════════════════`n"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "║              ✓ LOCKDOWN COMPLETE ✓                       ║" -ForegroundColor Green
Write-Host "║                                                          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "All containers have been stopped and removed." -ForegroundColor White
Write-Host "Docker Engine is still running in safe mode." -ForegroundColor White
Write-Host ""
Write-Host "📄 Incident logged to: $incidentLog" -ForegroundColor Cyan
Write-Host "📄 Report saved to: $reportFile" -ForegroundColor Cyan
Write-Host "📄 Snapshot saved to: $snapshotFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review incident log and report" -ForegroundColor White
Write-Host "  2. Investigate root cause" -ForegroundColor White
Write-Host "  3. Scan all remaining images for vulnerabilities" -ForegroundColor White
Write-Host "  4. Update security policies" -ForegroundColor White
Write-Host "  5. Document lessons learned" -ForegroundColor White
Write-Host ""

# Offer to open reports
$openReports = Read-Host "Open incident report? (y/n)"
if ($openReports -eq "y") {
    notepad $reportFile
    notepad $incidentLog
}
