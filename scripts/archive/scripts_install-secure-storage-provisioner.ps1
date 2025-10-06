# Install Secure Storage Provisioner for Kubernetes
# Date: 2025-09-29
# Purpose: Replace vulnerable docker/desktop-storage-provisioner with Rancher Local Path Provisioner

Write-Host "=== Secure Storage Provisioner Installation ===" -ForegroundColor Cyan
Write-Host ""

# Check if kubectl is available
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$kubectlExists = Get-Command kubectl -ErrorAction SilentlyContinue

if (-not $kubectlExists) {
    Write-Host "✗ kubectl not found. Please enable Kubernetes in Docker Desktop." -ForegroundColor Red
    Write-Host "  Settings → Kubernetes → Enable Kubernetes" -ForegroundColor Gray
    exit 1
}

Write-Host "✓ kubectl found" -ForegroundColor Green

# Check if Kubernetes is running
Write-Host "Checking Kubernetes cluster..." -ForegroundColor Yellow
$clusterInfo = kubectl cluster-info 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Kubernetes cluster not running" -ForegroundColor Red
    Write-Host "  Enable Kubernetes in Docker Desktop Settings" -ForegroundColor Gray
    exit 1
}

Write-Host "✓ Kubernetes cluster is running" -ForegroundColor Green
Write-Host ""

# Show current storage classes
Write-Host "Current storage classes:" -ForegroundColor Cyan
kubectl get storageclass
Write-Host ""

# Ask user which option to install
Write-Host "Select storage provisioner to install:" -ForegroundColor Cyan
Write-Host "  1. Rancher Local Path Provisioner (Recommended)" -ForegroundColor White
Write-Host "  2. Keep Docker Desktop built-in (hostpath)" -ForegroundColor White
Write-Host "  3. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Installing Rancher Local Path Provisioner..." -ForegroundColor Yellow
        Write-Host ""
        
        # Download and apply manifest
        $manifestUrl = "https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.32/deploy/local-path-storage.yaml"
        
        Write-Host "Applying manifest from: $manifestUrl" -ForegroundColor Gray
        kubectl apply -f $manifestUrl
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Installation failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "Waiting for provisioner to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Check deployment status
        Write-Host ""
        Write-Host "Deployment status:" -ForegroundColor Cyan
        kubectl -n local-path-storage get pods
        
        Write-Host ""
        Write-Host "Storage classes:" -ForegroundColor Cyan
        kubectl get storageclass
        
        Write-Host ""
        Write-Host "✓ Rancher Local Path Provisioner installed successfully" -ForegroundColor Green
        Write-Host ""
        Write-Host "To set as default storage class, run:" -ForegroundColor Yellow
        Write-Host '  kubectl patch storageclass local-path -p ''{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}''' -ForegroundColor Gray
        Write-Host '  kubectl patch storageclass hostpath -p ''{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}''' -ForegroundColor Gray
        Write-Host ""
        Write-Host "View logs with:" -ForegroundColor Yellow
        Write-Host "  kubectl -n local-path-storage logs -f -l app=local-path-provisioner" -ForegroundColor Gray
    }
    
    "2" {
        Write-Host ""
        Write-Host "Keeping Docker Desktop built-in storage provisioner" -ForegroundColor Green
        Write-Host ""
        Write-Host "The default 'hostpath' storage class is already configured." -ForegroundColor White
        Write-Host "This is maintained automatically by Docker Desktop." -ForegroundColor White
    }
    
    "3" {
        Write-Host ""
        Write-Host "Installation cancelled" -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Test with a PersistentVolumeClaim:" -ForegroundColor White
Write-Host "   See: e:\Projects\Development\docs\storage-provisioner-security-guide.md" -ForegroundColor Gray
Write-Host "2. Review the full security guide" -ForegroundColor White
Write-Host "3. Run cleanup script to remove vulnerable images" -ForegroundColor White
Write-Host "   .\scripts\cleanup-vulnerable-images.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
