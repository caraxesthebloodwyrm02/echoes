# Health Monitoring System v2.0

## Overview

The Unified Platform API provides comprehensive health monitoring for three integrated platforms:
- **Echoes** (`D:\realtime`) - Development platform with API gateway
- **Turbo** (`D:\realtime\turbobookshelf`) - Bias detection Glimpse
- **Glimpse** (`D:\realtime`) - Research and trajectory analysis

## API Endpoints

### Root Endpoint
```
GET /
```
Returns API status and available endpoints.

**Response:**
```json
{
  "message": "Unified Platform API",
  "version": "2.0.0",
  "endpoints": ["/api/health", "/api/health/simple"]
}
```

### Comprehensive Health Check
```
GET /api/health
```
Detailed health status for all platforms including system metrics.

**Timeout:** 10 seconds
**Response (200 OK):**
```json
{
  "status": "healthy",
  "details": {
    "echoes": {
      "healthy": true,
      "message": "Key file found: D:\\realtime\\api\\unified_gateway.py",
      "platform": "echoes"
    },
    "turbo": {
      "healthy": true,
      "message": "Key file found: D:\\realtime\\turbobookshelf\\engines\\insights\\bias.py",
      "platform": "turbo"
    },
    "glimpse": {
      "healthy": true,
      "message": "Key file found: D:\\realtime\\research\\glimpse\\overview.txt",
      "platform": "glimpse"
    },
    "system": {
      "cpu_usage": 9.1,
      "memory_usage": 58.8,
      "disk_usage": 45.8,
      "disk_free_gb": 196.6
    }
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": {
    "status": "degraded",
    "healthy_platforms": 2,
    "total_platforms": 3,
    "details": { ... }
  }
}
```

### Simple Health Check
```
GET /api/health/simple
```
Lightweight check for load balancers (verifies Turbo platform only).

**Timeout:** 5 seconds
**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "Primary platform unavailable"
}
```

## Platform Requirements

Each platform requires specific key files to pass health checks:

| Platform | Root Path | Key File(s) |
|----------|-----------|-------------|
| **Echoes** | `D:\realtime` | `api/unified_gateway.py` OR `packages/core/config/config.py` |
| **Turbo** | `D:\realtime\turbobookshelf` | `engines/insights/bias.py` OR `TurboBookshelf/engines/insights/bias.py` |
| **Glimpse** | `D:\realtime` | `research/glimpse/overview.txt` |

## Running the Server

### Start the API Server
```bash
uvicorn api.unified_gateway:app --reload --host 127.0.0.1 --port 8000
```

### Test Endpoints
```bash
# Root endpoint
curl http://127.0.0.1:8000/

# Comprehensive health check
curl http://127.0.0.1:8000/api/health

# Simple health check
curl http://127.0.0.1:8000/api/health/simple
```

## Automated Monitoring

### Using the Monitoring Script

The `scripts/health_monitor.py` script provides automated health checks with detailed reporting.

**Prerequisites:**
```bash
pip install requests
```

**Run the script:**
```bash
python scripts/health_monitor.py
```

**Sample Output:**
```
[2025-10-18 02:47:00] Starting unified platform health monitor

Simple Health Check
  Endpoint: http://127.0.0.1:8000/api/health/simple
  Status : 200
  Time   : 0.12s
  Body   : {'status': 'healthy'}

Detailed Health Check
  Endpoint: http://127.0.0.1:8000/api/health
  Status : 200
  Time   : 1.45s
  Body   : {'status': 'healthy', 'details': {...}}

Overall Result
  ✅ SYSTEM HEALTHY
```

### Scheduled Monitoring

**Windows Task Scheduler:**
```powershell
# Run every 5 minutes
schtasks /create /tn "Health Monitor" /tr "python D:\realtime\scripts\health_monitor.py" /sc minute /mo 5
```

**Linux/Mac Cron:**
```bash
# Add to crontab (every 5 minutes)
*/5 * * * * cd /path/to/realtime && python scripts/health_monitor.py >> logs/health_monitor.log 2>&1
```

## Configuration

Platform paths are configured in `packages/core/config/config.py`:

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class UnifiedConfig(BaseSettings):
    echoes_root: Path = Path("D:/realtime")
    turbo_root: Path = Path("D:/realtime/turbobookshelf")
    glimpse_root: Path = Path("D:/realtime")

    class Config:
        env_file = ".env"
        extra = "ignore"
```

### Environment Variables

Create a `.env` file to override defaults:
```bash
ECHOES_ROOT=E:/Projects/Development
TURBO_ROOT=D:/TurboBookshelf
GLIMPSE_ROOT=D:/realtime
```

## Troubleshooting

### Issue: "Service unhealthy" response

**Check platform paths:**
```bash
# Verify directories exist
dir D:\realtime
dir D:\realtime\turbobookshelf
dir D:\realtime\research\glimpse
```

**Check key files:**
```bash
dir D:\realtime\api\unified_gateway.py
dir D:\realtime\turbobookshelf\engines\insights\bias.py
dir D:\realtime\research\glimpse\overview.txt
```

**Review logs:**
Check the server console output for detailed error messages showing which files were searched.

### Issue: Permission denied errors

**Grant access to directories:**
```powershell
icacls "D:\realtime" /grant "Users:(OI)(CI)F" /t
icacls "D:\realtime\turbobookshelf" /grant "Users:(OI)(CI)F" /t
```

### Issue: Server won't start

**Check port availability:**
```bash
netstat -an | findstr 8000
```

**Kill existing processes:**
```powershell
taskkill /f /im uvicorn.exe
```

## CORS Configuration

The API includes permissive CORS settings for development and dashboard integration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production recommendation:** Replace `allow_origins=["*"]` with specific domains.

## Integration Examples

### Python Client
```python
import requests

response = requests.get("http://127.0.0.1:8000/api/health")
if response.status_code == 200:
    health = response.json()
    print(f"Status: {health['status']}")
    print(f"Platforms: {health['details'].keys()}")
```

### JavaScript/Fetch
```javascript
fetch('http://127.0.0.1:8000/api/health')
  .then(response => response.json())
  .then(data => {
    console.log('Health status:', data.status);
    console.log('System metrics:', data.details.system);
  });
```

### PowerShell
```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"
Write-Host "Status: $($response.status)"
Write-Host "CPU: $($response.details.system.cpu_usage)%"
```

## Metrics Reference

### System Metrics

| Metric | Description | Glimpse |
|--------|-------------|------|
| `cpu_usage` | Current CPU utilization | Percentage (0-100) |
| `memory_usage` | RAM utilization | Percentage (0-100) |
| `disk_usage` | C: drive utilization | Percentage (0-100) |
| `disk_free_gb` | Available disk space | Gigabytes |

### Platform Health

Each platform returns:
- `healthy` (boolean) - Overall health status
- `message` (string) - Diagnostic message
- `platform` (string) - Platform identifier
- `searched_files` (array, optional) - Files checked if unhealthy
- `error` (string, optional) - Exception details if failed

## Version History

### v2.0.0 (2025-10-18)
- ✅ Added CORS middleware for frontend integration
- ✅ Implemented `/api/health/simple` endpoint for load balancers
- ✅ Enhanced diagnostics with searched file lists
- ✅ Added system metrics (CPU, memory, disk)
- ✅ Created automated monitoring script
- ✅ Improved error handling and permission checks

### v1.0.0 (2025-10-17)
- Initial release with basic health checks

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify platform paths in `packages/core/config/config.py`
3. Ensure all key files exist at expected locations
4. Review this README's troubleshooting section

---

**Status:** Production-ready ✅
**Last Updated:** 2025-10-18
**Maintainer:** Unified Platform Team
