# Storage Provisioner Quick Reference

## Current Status

✅ **Docker Desktop:** v4.47.0 (Latest)  
⚠️ **Old Image:** `docker/desktop-storage-provisioner:v2.0` (97 CVEs)  
✅ **Built-in:** `hostpath` storage class (active)

---

## Quick Commands

### Check Current Setup
```powershell
# Docker version
docker version

# Kubernetes cluster
kubectl cluster-info

# Storage classes
kubectl get storageclass

# Check for vulnerable images
docker images | grep storage-provisioner
```

### Cleanup Vulnerable Image
```powershell
# Automated cleanup
.\scripts\cleanup-vulnerable-images.ps1

# Manual removal
docker rmi docker/desktop-storage-provisioner:v2.0
```

### Install Secure Alternative
```powershell
# Interactive installer
.\scripts\install-secure-storage-provisioner.ps1

# Manual install (Rancher Local Path)
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.32/deploy/local-path-storage.yaml

# Verify installation
kubectl -n local-path-storage get pods
```

### Test Storage
```powershell
# Apply test PVC
kubectl apply -f kubernetes/examples/test-pvc.yaml

# Check status
kubectl get pvc
kubectl get pod test-pod

# View logs
kubectl logs test-pod

# Cleanup
kubectl delete -f kubernetes/examples/test-pvc.yaml
```

---

## Storage Class Comparison

| Feature | Docker Desktop (hostpath) | Rancher Local Path |
|---------|--------------------------|-------------------|
| **Automatic** | ✅ Built-in | ⚠️ Requires install |
| **Security** | ✅ Updated with Desktop | ✅ Actively maintained |
| **CVEs** | None (v4.47.0) | None (v0.0.32) |
| **Features** | Basic | Advanced config |
| **Multi-node** | ❌ Single node only | ✅ Supported |
| **Production** | ❌ Dev only | ⚠️ Local dev only |

---

## Decision Tree

```
Do you use Kubernetes PVCs locally?
│
├─ No → Use Docker Desktop built-in (no action needed)
│
└─ Yes → Do you need advanced features?
         │
         ├─ No → Use Docker Desktop built-in
         │
         └─ Yes → Install Rancher Local Path Provisioner
```

---

## Troubleshooting

### PVC Stuck in Pending
```powershell
# Check events
kubectl describe pvc <pvc-name>

# Check provisioner logs (if Rancher installed)
kubectl -n local-path-storage logs -l app=local-path-provisioner
```

### Storage Class Not Found
```powershell
# List available classes
kubectl get storageclass

# Verify provisioner is running
kubectl -n local-path-storage get pods
```

### Pod Can't Mount Volume
```powershell
# Check PVC binding
kubectl get pvc

# Check pod events
kubectl describe pod <pod-name>

# Verify volume exists
kubectl get pv
```

---

## Security Checklist

- [ ] Docker Desktop updated to v4.47.0+
- [ ] Old `docker/desktop-storage-provisioner:v2.0` removed
- [ ] No containers using vulnerable images
- [ ] Using secure storage class (hostpath or local-path)
- [ ] Regular image scanning enabled
- [ ] Monthly Docker Desktop updates scheduled

---

## Files Created

```
e:\Projects\Development\
├── docs\
│   ├── storage-provisioner-security-guide.md    (Full guide)
│   └── storage-provisioner-quick-ref.md         (This file)
├── scripts\
│   ├── cleanup-vulnerable-images.ps1            (Remove old images)
│   └── install-secure-storage-provisioner.ps1   (Install Rancher)
└── kubernetes\
    └── examples\
        └── test-pvc.yaml                        (Test PVC/Pod)
```

---

## Resources

- **Full Guide:** `docs\storage-provisioner-security-guide.md`
- **Rancher Repo:** https://github.com/rancher/local-path-provisioner
- **Docker Desktop:** https://docs.docker.com/desktop/release-notes/
- **Kubernetes Storage:** https://kubernetes.io/docs/concepts/storage/

---

**Last Updated:** 2025-09-29  
**Next Review:** Monthly (with Docker Desktop updates)
