# Storage Provisioner Security Guide

**Date:** 2025-09-29
**Issue:** `docker/desktop-storage-provisioner:v2.0` contains 97 CVEs (10 critical)
**Your Docker Desktop:** v4.47.0 (Current - Already up-to-date ✅)

---

## Executive Summary

The old `docker/desktop-storage-provisioner:v2.0` image on your system is from 2021 and has critical security vulnerabilities. However, **your Docker Desktop (v4.47.0) is already up-to-date** and uses a newer internal provisioner. The v2.0 image is likely a cached artifact that Docker Desktop no longer uses.

---

## 1. Docker Desktop Status ✅

### Current Installation
```powershell
Docker Desktop: 4.47.0 (September 2025)
Docker Glimpse: 28.4.0
Go version: go1.24.7
containerd: 1.7.27
```

**Action Required:** None - You're already running the latest version.

### What Docker Desktop Already Does
- Docker Desktop 4.47.0 includes updated internal Kubernetes components
- The storage provisioner is managed automatically
- Security updates are bundled with Desktop releases

---

## 2. Clean Up Old Images

The vulnerable `docker/desktop-storage-provisioner:v2.0` image is likely unused. Remove it:

```powershell
# Check if any containers are using it
docker ps -a --filter ancestor=docker/desktop-storage-provisioner:v2.0

# If no containers found, remove the image
docker rmi docker/desktop-storage-provisioner:v2.0

# Verify removal
docker images | grep desktop-storage-provisioner
```

**Safe to remove:** If no containers are running, this is just cached metadata from Docker Desktop's internal operations.

---

## 3. Secure Alternatives (If Using Kubernetes)

If you're running Kubernetes workloads that need dynamic storage provisioning, use these modern alternatives:

### Option A: Rancher Local Path Provisioner (Recommended) 🌟

**Pros:**
- Actively maintained (latest: v0.0.32, 2024)
- No known CVEs in current version
- Simple, battle-tested
- Works with Docker Desktop Kubernetes

**Installation:**
```bash
# Enable Kubernetes in Docker Desktop first
# Settings → Kubernetes → Enable Kubernetes

# Install stable version
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.32/deploy/local-path-storage.yaml

# Verify installation
kubectl -n local-path-storage get pod

# Set as default storage class (optional)
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

**Usage Example:**
```yaml
# pvc-example.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 5Gi
```

### Option B: Kubernetes CSI Hostpath Driver

**Pros:**
- Official Kubernetes SIG project
- Supports snapshots
- Multi-node clusters

**Installation:**
```bash
# For Docker Desktop Kubernetes
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-host-path/master/deploy/kubernetes-latest/hostpath/csi-hostpath-plugin.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-host-path/master/deploy/kubernetes-latest/hostpath/csi-hostpath-storageclass.yaml
```

### Option C: Docker Desktop Built-in (Default)

**If you don't need custom provisioning:**
- Docker Desktop Kubernetes includes a built-in storage class
- Automatically updated with Desktop releases
- No manual configuration needed

```bash
# Check existing storage classes
kubectl get storageclass

# Should show 'hostpath' (default)
```

---

## 4. Verification Steps

### Check for Running Vulnerable Containers
```powershell
# List all images with CVE info
docker scout cves docker/desktop-storage-provisioner:v2.0

# Check what's actually running in Kubernetes
kubectl get pods --all-namespaces -o wide

# Verify storage classes
kubectl get sc
```

### Monitor Image Usage
```powershell
# See which images are in use
docker ps --format "table {{.Image}}\t{{.Status}}"

# List all images sorted by date
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
```

---

## 5. Security Best Practices

### Regular Maintenance
1. **Update Docker Desktop monthly** (Settings → Software Updates)
2. **Scan images before deployment:**
   ```powershell
   docker scout cves <image-name>
   ```
3. **Remove unused images:**
   ```powershell
   docker image prune -a --filter "until=720h"  # Older than 30 days
   ```

### For Production Environments
- Don't use Docker Desktop's built-in Kubernetes for production
- Use managed Kubernetes (AKS, EKS, GKE) with CSI drivers
- Implement image scanning in CI/CD pipelines
- Use admission controllers to block vulnerable images

---

## 6. Quick Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| **Just developing locally** | Use Docker Desktop built-in (no action needed) |
| **Need PVC in local K8s** | Install Rancher Local Path Provisioner |
| **Testing K8s features** | Install CSI Hostpath Driver |
| **Production workload** | Use cloud provider's storage class |
| **Security-critical** | Scan all images, remove v2.0 |

---

## 7. Immediate Action Items

- [ ] Remove old `docker/desktop-storage-provisioner:v2.0` image
- [ ] Verify no containers use the old provisioner
- [ ] If using Kubernetes locally, install Rancher Local Path Provisioner
- [ ] Set up monthly Docker Desktop update reminders
- [ ] Scan all local images for CVEs

---

## 8. Resources

- [Docker Desktop Release Notes](https://docs.docker.com/desktop/release-notes/)
- [Rancher Local Path Provisioner](https://github.com/rancher/local-path-provisioner)
- [Kubernetes CSI Documentation](https://kubernetes-csi.github.io/)
- [Docker Scout Documentation](https://docs.docker.com/scout/)

---

## Exit Criteria ✓

This issue is resolved when:
1. ✅ Docker Desktop is version 4.47.0 or newer (Complete)
2. ⏳ Old vulnerable images are removed
3. ⏳ (Optional) Modern storage provisioner installed for K8s workloads
4. ⏳ No critical CVEs in running containers
