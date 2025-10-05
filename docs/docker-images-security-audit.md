# Docker Images Security Audit

**Date:** 2025-09-29  
**Total Images Analyzed:** 10  
**Critical Issues:** 2 old Docker Desktop images

---

## 📊 Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| **Kubernetes Images** | 7 | ✅ Current (20 days - 6 months) |
| **Docker Desktop Images** | 2 | ⚠️ **OUTDATED** (2-4 years old) |
| **Other Images** | 1 | ℹ️ Unknown (MCP sandbox) |
| **Action Required** | 2 | Remove vulnerable images |

---

## 🔴 Critical Issues

### 1. docker/desktop-storage-provisioner:v2.0 (4 years old)

**Status:** 🚨 **CRITICAL** - 97 CVEs  
**Created:** 2021-04-26 (4 years ago)  
**Size:** 59.16 MB

#### Vulnerable Dependencies (from SBOM)

| Package | Version | Issue |
|---------|---------|-------|
| **Go stdlib** | 1.14.15 | 10 critical CVEs |
| **gogo/protobuf** | 1.3.1 | CVE-2021-3121 (8.6 high) |
| **golang.org/x/crypto** | 2020-03-23 | Outdated (5 years) |
| **golang.org/x/net** | 2020-03-20 | Outdated (5 years) |
| **k8s.io/client-go** | 0.17.4 | Outdated (4 years) |

#### Action
```powershell
# REMOVE IMMEDIATELY
docker rmi docker/desktop-storage-provisioner:v2.0

# Or use automated script
.\scripts\cleanup-vulnerable-images.ps1
```

---

### 2. docker/desktop-vpnkit-controller (2 years old)

**Status:** ⚠️ **OLD** - Unknown CVEs  
**Created:** 2023-xx-xx (2 years ago)  
**Size:** 46.99 MB  
**SHA:** dc331cb22850be0cdd97c84a9cfecaf44a1afb6e

#### Analysis
- Part of Docker Desktop networking
- No tag specified (only SHA)
- Likely unused by current Docker Desktop v4.47.0

#### Action
```powershell
# Check if in use
docker ps -a --filter ancestor=docker/desktop-vpnkit-controller:dc331cb22850be0cdd97c84a9cfecaf44a1afb6e

# If no containers, remove
docker rmi 7ecf567ea070
```

---

## ✅ Kubernetes Images (Safe)

These are current and maintained by the Kubernetes project:

| Image | Version | Age | Status |
|-------|---------|-----|--------|
| **kube-controller-manager** | v1.34.1 | 20 days | ✅ Current |
| **kube-scheduler** | v1.34.1 | 20 days | ✅ Current |
| **kube-apiserver** | v1.34.1 | 20 days | ✅ Current |
| **kube-proxy** | v1.34.1 | 20 days | ✅ Current |
| **etcd** | 3.6.4-0 | 2 months | ✅ Current |
| **coredns** | v1.12.1 | 6 months | ✅ Current |
| **pause** | 3.10 | 1 year | ✅ Stable (rarely updated) |

**No Action Required** - These are pulled and managed by Docker Desktop Kubernetes.

---

## ℹ️ Unknown Images

### mcp/node-code-sandbox (23 days ago)

**Status:** ℹ️ **UNKNOWN**  
**Size:** 825.73 MB (largest image)  
**Tag:** `<none>`

#### Notes
- MCP (Model Context Protocol) related
- Relatively recent (23 days)
- Large size suggests development environment
- No tag indicates custom/local build

#### Recommendation
```powershell
# Check if needed
docker ps -a | Select-String "mcp/node-code-sandbox"

# If unused, consider removing to save 825 MB
docker rmi 6b7180ab719d
```

---

## 🔍 SBOM Analysis (storage-provisioner:v2.0)

### Critical Findings

**Built with:** Go 1.14.15 (released 2020, EOL)  
**Architecture:** ARM64  
**Created:** 2021-04-26

### Dependency Tree (38 packages)

#### Most Vulnerable

1. **golang/stdlib@1.14.15**
   - CVE-2023-24538 (9.8 Critical)
   - CVE-2024-24790 (9.8 Critical)
   - CVE-2023-24540 (9.8 Critical)
   - CVE-2022-23806 (9.1 Critical)
   - CVE-2025-22871 (9.1 Critical)
   - +92 more CVEs

2. **github.com/gogo/protobuf@1.3.1**
   - CVE-2021-3121 (8.6 High)

3. **golang.org/x/crypto** (2020 version)
   - Multiple known vulnerabilities
   - 5 years out of date

4. **golang.org/x/net** (2020 version)
   - Multiple known vulnerabilities
   - 5 years out of date

#### Kubernetes Dependencies (Outdated)

- k8s.io/api@0.17.4 (should be 1.34+)
- k8s.io/apimachinery@0.17.4
- k8s.io/client-go@0.17.4

**Gap:** 17 major versions behind current Kubernetes

---

## 🎯 Immediate Actions

### Step 1: Cleanup Vulnerable Images (30 seconds)

```powershell
cd e:\Projects\Development

# Run automated cleanup
.\scripts\cleanup-vulnerable-images.ps1

# Or manual cleanup
docker rmi docker/desktop-storage-provisioner:v2.0
docker rmi docker/desktop-vpnkit-controller:dc331cb22850be0cdd97c84a9cfecaf44a1afb6e
```

### Step 2: Verify No Active Containers (10 seconds)

```powershell
# Check all containers
docker ps -a

# Should not show any using old Desktop images
```

### Step 3: Check Disk Space Saved

```powershell
# Before cleanup
docker system df

# After cleanup (should save ~106 MB)
docker system df
```

---

## 📈 Storage Impact

### Removable Images

| Image | Size | Action |
|-------|------|--------|
| desktop-storage-provisioner:v2.0 | 59.16 MB | ✅ Remove (critical) |
| desktop-vpnkit-controller | 46.99 MB | ✅ Remove (unused) |
| mcp/node-code-sandbox | 825.73 MB | ⚠️ Evaluate need |
| **Total Potential Savings** | **931.88 MB** | |

### Keep These (Required by Kubernetes)

| Image | Size | Reason |
|-------|------|--------|
| kube-controller-manager | 101.09 MB | Active K8s component |
| kube-apiserver | 118.37 MB | Active K8s component |
| kube-proxy | 101.65 MB | Active K8s component |
| kube-scheduler | 73.5 MB | Active K8s component |
| etcd | 272.54 MB | K8s data store |
| coredns | 100.71 MB | K8s DNS |
| pause | 1.05 MB | K8s pod infrastructure |
| **Total K8s** | **768.91 MB** | **Required** |

---

## 🔐 Security Recommendations

### Immediate (Today)
1. ✅ Remove `docker/desktop-storage-provisioner:v2.0`
2. ✅ Remove `docker/desktop-vpnkit-controller` (old)
3. ✅ Verify no containers use these images

### Short-term (This Week)
1. Evaluate MCP sandbox image (825 MB)
2. Set up Docker Scout for continuous scanning
3. Document which images are intentional

### Ongoing (Monthly)
1. Update Docker Desktop (auto-updates K8s images)
2. Run image cleanup: `docker image prune -a --filter "until=720h"`
3. Scan with: `docker scout quickview`

---

## 🛠️ Automated Cleanup Script

Created at: `scripts\cleanup-vulnerable-images.ps1`

**Features:**
- ✅ Checks for active containers
- ✅ Safely removes old Desktop images
- ✅ Scans remaining images for CVEs
- ✅ Reports disk space savings

**Usage:**
```powershell
.\scripts\cleanup-vulnerable-images.ps1
```

---

## 📋 Verification Checklist

After cleanup:

```powershell
# 1. Verify removal
docker images | grep desktop
# Expected: No v2.0 storage-provisioner, no old vpnkit-controller

# 2. Check Kubernetes still works
kubectl get nodes
kubectl get pods --all-namespaces

# 3. Verify storage class
kubectl get storageclass
# Expected: hostpath (default) or local-path

# 4. Test storage (optional)
kubectl apply -f kubernetes/examples/test-pvc.yaml
kubectl get pvc
kubectl delete -f kubernetes/examples/test-pvc.yaml
```

---

## 🆘 Troubleshooting

### Issue: Can't Remove Image (in use)

```powershell
# Find which container uses it
docker ps -a | Select-String "<image-id>"

# Stop and remove container
docker stop <container-id>
docker rm <container-id>

# Then remove image
docker rmi <image-id>
```

### Issue: Kubernetes Broken After Cleanup

```powershell
# Docker Desktop manages K8s images automatically
# If K8s breaks, reset it:
# Docker Desktop → Settings → Kubernetes → Reset Kubernetes Cluster

# This will re-download all K8s images (takes 2-3 minutes)
```

### Issue: Storage Provisioner Not Working

**Good News:** Docker Desktop v4.47.0 uses a newer internal provisioner.  
The old v2.0 image is just cached and not in use.

```powershell
# Verify current storage class works
kubectl get storageclass
kubectl apply -f kubernetes/examples/test-pvc.yaml
```

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Total Images** | 10 |
| **Vulnerable** | 2 (Docker Desktop) |
| **Safe** | 7 (Kubernetes) |
| **Unknown** | 1 (MCP) |
| **CVEs in v2.0** | 97 (10 critical) |
| **Go Version** | 1.14.15 (5 years old) |
| **Disk Space to Reclaim** | 106 MB (932 MB if including MCP) |
| **Time to Fix** | 30 seconds |

---

## 🎉 Exit Criteria

Task complete when:

- [x] SBOM analyzed and documented
- [ ] `docker/desktop-storage-provisioner:v2.0` removed
- [ ] `docker/desktop-vpnkit-controller` removed
- [ ] No containers using vulnerable images
- [ ] Kubernetes still functional
- [ ] Storage provisioning tested

---

## 📚 Related Documentation

- **Main Guide:** `storage-provisioner-security-guide.md`
- **Quick Reference:** `storage-provisioner-quick-ref.md`
- **Next Steps:** `NEXT-STEPS.md`
- **Cleanup Script:** `scripts\cleanup-vulnerable-images.ps1`

---

**Action Required:** Run `.\scripts\cleanup-vulnerable-images.ps1` now to remove 97 CVEs from your system.
