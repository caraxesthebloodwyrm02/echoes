# Monthly Security Audit
# Comprehensive security scan and cleanup
# Date: 2025-09-29

$ErrorActionPreference = "Continue"
$date = Get-Date -Format "yyyy-MM-dd-HHmm"
$logDir = "E:\Projects\Development\logs"
$reportDir = "E:\Projects\Development\logs\monthly-reports"

# Create directories
foreach ($dir in @($logDir, $reportDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

$reportFile = "$reportDir\audit-$date.txt"

Write-Host "=== Monthly Security Audit ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

function Write-AuditOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
    Add-Content -Path $reportFile -Value $Message
}

# Check if Docker is running
$dockerRunning = docker version 2>&1 | Select-String "Server:"
if (-not $dockerRunning) {
    Write-AuditOutput "❌ Docker Desktop is not running" "Red"
    Write-AuditOutput "Start Docker Desktop to perform audit." "Gray"
    exit 1
}

# Header
Write-AuditOutput "╔════════════════════════════════════════════════════════════╗" "Cyan"
Write-AuditOutput "║           MONTHLY DOCKER SECURITY AUDIT                    ║" "Cyan"
Write-AuditOutput "║           $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')                           ║" "Cyan"
Write-AuditOutput "╚════════════════════════════════════════════════════════════╝" "Cyan"
Write-AuditOutput ""

# 1. System Information
Write-AuditOutput "1. SYSTEM INFORMATION" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━━━━━" "Yellow"
$dockerVersion = docker version --format "json" | ConvertFrom-Json
Write-AuditOutput "   Docker Version: $($dockerVersion.Server.Version)" "White"
Write-AuditOutput "   OS: $($dockerVersion.Server.Os)/$($dockerVersion.Server.Arch)" "White"
Write-AuditOutput "   API Version: $($dockerVersion.Server.ApiVersion)" "White"
Write-AuditOutput ""

# 2. Image Inventory
Write-AuditOutput "2. IMAGE INVENTORY" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━" "Yellow"
$images = docker images --format "{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}|{{.CreatedAt}}"
$imageCount = ($images | Measure-Object).Count
Write-AuditOutput "   Total Images: $imageCount" "White"
Write-AuditOutput ""
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | ForEach-Object {
    Write-AuditOutput "   $_" "Gray"
}
Write-AuditOutput ""

# 3. Full CVE Scan
Write-AuditOutput "3. VULNERABILITY SCAN (CVE)" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━" "Yellow"
$totalCritical = 0
$totalHigh = 0
$totalMedium = 0

$images | ForEach-Object {
    $image = ($_ -split '\|')[0]
    Write-AuditOutput "   Scanning: $image" "Gray"
    
    try {
        $cveOutput = docker scout cves $image 2>&1 | Out-String
        
        # Extract CVE counts
        if ($cveOutput -match "(\d+)\s+critical") { $totalCritical += [int]$matches[1] }
        if ($cveOutput -match "(\d+)\s+high") { $totalHigh += [int]$matches[1] }
        if ($cveOutput -match "(\d+)\s+medium") { $totalMedium += [int]$matches[1] }
        
        # Save detailed report
        $cveOutput | Out-File "$reportDir\cve-$($image.Replace('/','-').Replace(':','-'))-$date.txt"
        
        if ($cveOutput -match "critical") {
            Write-AuditOutput "     ❌ CRITICAL vulnerabilities found!" "Red"
        } elseif ($cveOutput -match "high") {
            Write-AuditOutput "     ⚠️  High vulnerabilities found" "Yellow"
        } else {
            Write-AuditOutput "     ✓ No critical issues" "Green"
        }
    } catch {
        Write-AuditOutput "     ℹ️  Unable to scan (Docker Scout required)" "Gray"
    }
}

Write-AuditOutput ""
Write-AuditOutput "   SUMMARY:" "White"
Write-AuditOutput "   Critical: $totalCritical" $(if ($totalCritical -gt 0) { "Red" } else { "Green" })
Write-AuditOutput "   High: $totalHigh" $(if ($totalHigh -gt 0) { "Yellow" } else { "Green" })
Write-AuditOutput "   Medium: $totalMedium" "Gray"
Write-AuditOutput ""

# 4. Cleanup Old Images
Write-AuditOutput "4. CLEANUP OPERATIONS" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━━━━" "Yellow"

# Dangling images
Write-AuditOutput "   Removing dangling images..." "Gray"
$danglingRemoved = docker image prune -f 2>&1
Write-AuditOutput "   $danglingRemoved" "Gray"

# Old images (60+ days)
Write-AuditOutput "   Removing images older than 60 days..." "Gray"
$oldRemoved = docker image prune -a --filter "until=1440h" -f 2>&1
Write-AuditOutput "   $oldRemoved" "Gray"

# System cleanup
Write-AuditOutput "   System cleanup..." "Gray"
$systemClean = docker system prune -f 2>&1
Write-AuditOutput "   $systemClean" "Gray"
Write-AuditOutput ""

# 5. Disk Usage Analysis
Write-AuditOutput "5. DISK USAGE ANALYSIS" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━━━━━" "Yellow"
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}" | ForEach-Object {
    Write-AuditOutput "   $_" "White"
}
Write-AuditOutput ""

# 6. Container Audit
Write-AuditOutput "6. CONTAINER AUDIT" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━" "Yellow"
$allContainers = docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
if (($allContainers | Measure-Object).Count -gt 1) {
    $allContainers | ForEach-Object { Write-AuditOutput "   $_" "Gray" }
} else {
    Write-AuditOutput "   No containers found" "Green"
}
Write-AuditOutput ""

# 7. Network Audit
Write-AuditOutput "7. NETWORK AUDIT" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━" "Yellow"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" | ForEach-Object {
    Write-AuditOutput "   $_" "Gray"
}
Write-AuditOutput ""

# 8. Volume Audit
Write-AuditOutput "8. VOLUME AUDIT" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━" "Yellow"
docker volume ls --format "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}" | ForEach-Object {
    Write-AuditOutput "   $_" "Gray"
}
Write-AuditOutput ""

# 9. Security Recommendations
Write-AuditOutput "9. SECURITY RECOMMENDATIONS" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━" "Yellow"

$recommendations = @()

if ($totalCritical -gt 0) {
    $recommendations += "   🚨 CRITICAL: $totalCritical critical vulnerabilities - IMMEDIATE ACTION REQUIRED"
}
if ($totalHigh -gt 5) {
    $recommendations += "   ⚠️  HIGH: $totalHigh high vulnerabilities - Review and update images"
}
if ($imageCount -gt 15) {
    $recommendations += "   ℹ️  INFO: $imageCount images present - Consider cleanup"
}

# Check for old Kubernetes images
$k8sImages = docker images --format "{{.Repository}}:{{.Tag}}|{{.CreatedAt}}" | Select-String "registry.k8s.io"
$oldK8s = $k8sImages | Select-String "2024-" 
if ($oldK8s) {
    $recommendations += "   ℹ️  INFO: Kubernetes images from 2024 detected - Update Docker Desktop"
}

if ($recommendations.Count -eq 0) {
    Write-AuditOutput "   ✅ No critical recommendations - System is secure" "Green"
} else {
    $recommendations | ForEach-Object { Write-AuditOutput $_ "Yellow" }
}
Write-AuditOutput ""

# 10. Action Items
Write-AuditOutput "10. ACTION ITEMS FOR NEXT MONTH" "Yellow"
Write-AuditOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "Yellow"
Write-AuditOutput "   [ ] Review all critical CVEs" "White"
Write-AuditOutput "   [ ] Update Docker Desktop if new version available" "White"
Write-AuditOutput "   [ ] Remove unused images and containers" "White"
Write-AuditOutput "   [ ] Review and rotate secrets/credentials" "White"
Write-AuditOutput "   [ ] Test backup/restore procedures" "White"
Write-AuditOutput "   [ ] Review access logs (if applicable)" "White"
Write-AuditOutput ""

# Summary
Write-AuditOutput "╔════════════════════════════════════════════════════════════╗" "Cyan"
Write-AuditOutput "║                    AUDIT COMPLETE                          ║" "Cyan"
Write-AuditOutput "╚════════════════════════════════════════════════════════════╝" "Cyan"
Write-AuditOutput ""
Write-AuditOutput "Report saved to: $reportFile" "Green"
Write-AuditOutput "Detailed CVE reports: $reportDir\cve-*.txt" "Green"
Write-AuditOutput ""
Write-AuditOutput "Next audit: $(Get-Date).AddMonths(1).ToString('yyyy-MM-dd')" "Gray"
Write-AuditOutput ""

# Offer to open report
$openReport = Read-Host "Open audit report? (y/n)"
if ($openReport -eq "y") {
    notepad $reportFile
}


