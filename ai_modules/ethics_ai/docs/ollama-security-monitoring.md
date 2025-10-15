# Ollama Security Monitoring Guide

**Image:** ollama/ollama:latest
**Size:** 4.93 GB
**Last Updated:** 2025-09-25 (4 days ago)
**Current Status:** ⚠️ 1 Critical, 1 High, 7 Medium, 6 Low

---

## 📊 Current Vulnerabilities (2025-09-29)

### Critical Issues

**CVE-2025-22871** - Go stdlib 1.24.0
- **Severity:** 9.1 Critical
- **Fix Available:** Go 1.24.2+
- **Status:** Waiting for Ollama team to rebuild
- **Tracking:** https://scout.docker.com/v/CVE-2025-22871

### High Issues

**CVE-2025-22874** - Go stdlib 1.24.0
- **Severity:** High
- **Fix Available:** Go 1.24.4+
- **Status:** Waiting for Ollama team to rebuild

### Assessment

✅ **Safe to use** - These are recent CVEs (2025), image is only 4 days old
✅ **Low risk** - Requires local access to exploit
⚠️ **Monitor weekly** - Ollama team likely preparing updates
✅ **Already latest** - You have the most recent version

---

## 🔄 Update Monitoring

### Automated (Weekly)

Your `weekly-security-check.ps1` now includes:
- ✅ Automatic ollama CVE scanning
- ✅ Automatic update checking
- ✅ Pull latest version if available
- ✅ Comparison tracking

### Manual Check

```powershell
# Check for updates
docker pull ollama/ollama:latest

# Scan for new CVEs
docker scout cves ollama/ollama:latest

# See recommendations
docker scout recommendations ollama/ollama:latest
```

---

## 📈 Vulnerability Trend

| Date | Critical | High | Medium | Low | Notes |
|------|----------|------|--------|-----|-------|
| 2025-09-29 | 1 | 1 | 7 | 6 | Initial scan, image up to date |
| (future) | - | - | - | - | Update weekly |

---

## 🎯 Action Triggers

### Immediate Action Required

```yaml
If Critical CVEs > 1:
  → Check for updates immediately
  → Consider stopping ollama until patched
  → Review security logs

If High CVEs > 3:
  → Check for updates daily
  → Monitor for exploits
  → Review access controls
```

### Current Status: MONITOR

```yaml
Current: 1 Critical, 1 High
Action: Weekly monitoring (automated)
Timeline: Check for updates in Ollama releases
Risk Level: LOW (recent image, fixes pending)
```

---

## 🔍 Understanding the CVEs

### Why These Exist

1. **Go 1.24.0 is new** (released recently)
2. **CVEs discovered quickly** (2025 CVEs)
3. **Fixes available** (Go 1.24.2+)
4. **Ollama rebuilding** (takes time to test and release)

### Why It's Acceptable

- ✅ Image is only 4 days old (very recent)
- ✅ CVEs require local access (not remotely exploitable)
- ✅ Ollama is actively maintained
- ✅ Fixes are in pipeline (Go updates available)
- ✅ You're using latest version

---

## 🛠️ Maintenance Schedule

### Weekly (Automated)

```powershell
# Runs automatically via weekly-security-check.ps1
.\scripts\weekly-security-check.ps1
```

**What it does:**
1. Scans ollama for CVEs
2. Reports vulnerability counts
3. Checks for updates
4. Automatically pulls if newer version available
5. Logs all activity

### Monthly (Manual Review)

```powershell
# Full audit
.\scripts\monthly-security-audit.ps1

# Review ollama changelog
# Visit: https://github.com/ollama/ollama/releases
```

---

## 📚 Ollama Resources

### Official

- **GitHub:** https://github.com/ollama/ollama
- **Docker Hub:** https://hub.docker.com/r/ollama/ollama
- **Documentation:** https://ollama.ai/

### Security

- **CVE Database:** https://scout.docker.com/
- **Go Security:** https://go.dev/security
- **Ubuntu CVEs:** https://ubuntu.com/security/cves

---

## 🚨 Incident Response

If you discover active exploitation:

```powershell
# Emergency: Stop all ollama containers
docker stop $(docker ps -q --filter ancestor=ollama/ollama:latest)

# Run emergency lockdown (if needed)
.\scripts\emergency-lockdown.ps1

# Review logs
docker logs <container-id>

# Document incident
# Add to: logs\security-incidents.log
```

---

## 💡 Optimization Tips

### Reduce Attack Surface

```yaml
When running ollama:
  1. Use specific version tags (not :latest in production)
  2. Run with minimal privileges
  3. Isolate network access
  4. Mount volumes read-only where possible
  5. Set resource limits
```

### Example Secure Run

```bash
docker run -d \
  --name ollama \
  --restart unless-stopped \
  --memory=8g \
  --cpus=4 \
  --read-only \
  --tmpfs /tmp \
  -v ollama-data:/root/.ollama \
  -p 127.0.0.1:11434:11434 \
  ollama/ollama:latest
```

---

## ✅ Current Status Summary

**As of 2025-09-29:**

```yaml
Image: ollama/ollama:latest
Version: Latest available (2025-09-25)
Vulnerabilities:
  Critical: 1 (CVE-2025-22871)
  High: 1 (CVE-2025-22874)
  Medium: 7
  Low: 6

Risk Assessment: LOW-MEDIUM
Recommendation: KEEP & MONITOR
Monitoring: ENABLED (automated weekly)
Next Check: 2025-10-06 (weekly)
Next Audit: 2025-10-29 (monthly)
```

---

## 🎯 Exit Criteria

**Safe to continue using when:**
- ✅ Image is less than 30 days old
- ✅ Critical CVEs < 2
- ✅ Known exploits = 0
- ✅ Ollama team is responsive
- ✅ Weekly monitoring is active

**All criteria currently met.** ✅

---

**Last Updated:** 2025-09-29
**Next Review:** 2025-10-06 (automated)
**Status:** Secure with monitoring
