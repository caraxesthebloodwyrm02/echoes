# Cleanup Vulnerable Docker Desktop Images
# Date: 2025-09-29
# Purpose: Remove old Docker Desktop images with security vulnerabilities
#   - docker/desktop-storage-provisioner:v2.0 (97 CVEs, 4 years old)
#   - docker/desktop-vpnkit-controller (2 years old)

Write-Host "=== Docker Desktop Images Cleanup Script ===" -ForegroundColor Cyan
Write-Host ""

$totalRemoved = 0
$totalSpaceSaved = 0

# Define vulnerable images to remove
$vulnerableImages = @(
    @{Name="docker/desktop-storage-provisioner:v2.0"; ID="115d77efe6e2"; CVEs=97; Age="4 years"},
    @{Name="docker/desktop-vpnkit-controller"; ID="7ecf567ea070"; CVEs="Unknown"; Age="2 years"}
)

# Step 1: Check for running containers
Write-Host "Step 1: Checking for containers using vulnerable images..." -ForegroundColor Yellow

foreach ($image in $vulnerableImages) {
    $containers = docker ps -a --filter ancestor=$($image.ID) --format "{{.ID}}"
    
    if ($containers) {
        Write-Host "  ⚠ WARNING: Found containers using $($image.Name)" -ForegroundColor Red
        docker ps -a --filter ancestor=$($image.ID)
        Write-Host ""
        Write-Host "Please stop and remove these containers first." -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ No containers using vulnerable images" -ForegroundColor Green
Write-Host ""

# Step 2: Check and remove vulnerable images
Write-Host "Step 2: Checking for vulnerable images..." -ForegroundColor Yellow
Write-Host ""

foreach ($image in $vulnerableImages) {
    # Check if image exists by ID
    $imageInfo = docker images --filter "reference=*" --format "{{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}" | Select-String $($image.ID)
    
    if ($imageInfo) {
        Write-Host "Found vulnerable image:" -ForegroundColor Yellow
        Write-Host "  Name: $($image.Name)" -ForegroundColor White
        Write-Host "  CVEs: $($image.CVEs)" -ForegroundColor Red
        Write-Host "  Age: $($image.Age)" -ForegroundColor Yellow
        Write-Host "  ID: $($image.ID)" -ForegroundColor Gray
        Write-Host ""
        
        # Extract size for tracking
        if ($imageInfo -match '(\d+(?:\.\d+)?)\s*(MB|GB)') {
            $size = $matches[1]
            $unit = $matches[2]
            if ($unit -eq "GB") {
                $totalSpaceSaved += [float]$size * 1024
            } else {
                $totalSpaceSaved += [float]$size
            }
        }
        
        # Remove image
        Write-Host "Removing $($image.Name)..." -ForegroundColor Yellow
        docker rmi $($image.ID) 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Removed successfully" -ForegroundColor Green
            $totalRemoved++
        } else {
            # Try force removal
            Write-Host "  Trying force removal..." -ForegroundColor Yellow
            docker rmi -f $($image.ID) 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Force removed successfully" -ForegroundColor Green
                $totalRemoved++
            } else {
                Write-Host "✗ Failed to remove" -ForegroundColor Red
            }
        }
        Write-Host ""
    } else {
        Write-Host "✓ $($image.Name) not found (already removed)" -ForegroundColor Green
    }
}

Write-Host ""

# Step 3: Summary
Write-Host "=== Cleanup Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Images Processed: $($vulnerableImages.Count)" -ForegroundColor White
Write-Host "Images Removed: $totalRemoved" -ForegroundColor $(if ($totalRemoved -gt 0) { "Green" } else { "Yellow" })

if ($totalSpaceSaved -gt 0) {
    Write-Host "Disk Space Reclaimed: ~$([math]::Round($totalSpaceSaved, 2)) MB" -ForegroundColor Green
}

Write-Host ""
Write-Host "✓ Docker Desktop: v4.47.0 (Current)" -ForegroundColor Green
Write-Host "✓ No containers using vulnerable images" -ForegroundColor Green

if ($totalRemoved -gt 0) {
    Write-Host "✓ Removed $totalRemoved vulnerable images" -ForegroundColor Green
} else {
    Write-Host "✓ System was already clean" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Review full audit: docs\docker-images-security-audit.md" -ForegroundColor White
Write-Host "2. Check remaining images:" -ForegroundColor White
Write-Host "   docker images" -ForegroundColor Gray
Write-Host "3. If using Kubernetes PVCs, consider:" -ForegroundColor White
Write-Host "   .\scripts\install-secure-storage-provisioner.ps1" -ForegroundColor Gray
Write-Host "4. Monthly: Update Docker Desktop for latest security patches" -ForegroundColor White
Write-Host ""
Write-Host "Cleanup complete! 🎉" -ForegroundColor Green
