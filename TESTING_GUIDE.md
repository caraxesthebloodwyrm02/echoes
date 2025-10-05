# Complete Testing Workflow

## 🎯 Step-by-Step Testing Guide

### 1. Start the Application
Choose one of these options:

**Option A: Docker (Recommended)**
`powershell
# Build and run with Docker
.\make.ps1 build
.\make.ps1 run
`

**Option B: Local Development**
`powershell
# Install and run locally
.\make.ps1 install
.\make.ps1 dev
`

### 2. Test API Endpoints

**Health Check:**
`powershell
curl http://localhost:8000/health
# Expected: {\
status\:\healthy\} or similar
`

**API Documentation:**
`powershell
curl http://localhost:8000/docs
# Should return HTML content
`

**OpenAPI Schema:**
`powershell
curl http://localhost:8000/openapi.json
# Should return JSON schema
`

**Authentication Test:**
`powershell
# Login
curl -X POST http://localhost:8000/api/auth/login \\
  -H 'Content-Type: application/json' \\
  -d '{\username\: \admin\, \password\: \admin123\}'

# Use token to access protected endpoint
curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/auth/me
`

### 3. Run Automated Tests
`powershell
.\make.ps1 test
`

### 4. Security Validation
`powershell
.\make.ps1 security
`

### 5. View Logs
`powershell
.\make.ps1 logs
`

### 6. Cleanup
`powershell
.\make.ps1 stop
.\make.ps1 clean
`

## ✅ Expected Results

- **API starts successfully** without import errors
- **Health endpoint responds** with status information
- **Authentication works** for admin/admin123
- **Protected endpoints** require valid tokens
- **Security scan passes** with minimal warnings
- **All endpoints documented** in OpenAPI schema

## 🔧 Troubleshooting

If Docker doesn't work:
1. Ensure Docker Desktop is running
2. Try: docker system prune -a to clean up
3. Fall back to local development with .\make.ps1 dev

If API doesn't respond:
1. Check if port 8000 is available
2. Verify no firewall blocking
3. Check application logs

Ready to test! 🚀
