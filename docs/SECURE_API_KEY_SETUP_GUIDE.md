# 🔐 SECURE API KEY SETUP GUIDE
# Echoes Assistant V2 - Environment Variables Only

## 🚨 SECURITY FIRST - DELETE ALL KEY FILES

### IMMEDIATE ACTION REQUIRED:
Run this command to securely delete any potential API key files:

```powershell
# Windows PowerShell - Run as Administrator
cd E:\Projects\Echoes

# Secure delete any .env files or key files
Remove-Item -Path "*.env" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*key*.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*secret*.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "*token*.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "config/keys.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "api_keys.json" -Force -ErrorAction SilentlyContinue

# Verify deletion
Get-ChildItem -Recurse -File | Where-Object { $_.Name -match "key|secret|token|api" -and $_.Name -notmatch "__pycache__|venv|\.git" }
```

## 🔑 SECURE API KEY SETUP VIA ENVIRONMENT VARIABLES

### Step 1: Set Environment Variables (Windows)

#### Option A: System Environment Variables (Recommended)
```powershell
# Run PowerShell as Administrator

# Open System Properties > Advanced > Environment Variables
# OR use these commands:

# Set OpenAI API Key
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-actual-openai-api-key-here', 'Machine')

# Set Cascade API Key (for Windsurf IDE authentication)
[System.Environment]::SetEnvironmentVariable('CASCAD_API_KEY', 'sk-ws-01-San-LQfCjNs-V2WokDFnzSXQftsn5MDQESIh_IucWyeIIHblAXy0YPHfBomv7_SfAN9S5D8PMKsqfuVatXMAVrEhiNdimA', 'Machine')

# Set Other API Keys (if needed)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-anthropic-key-here', 'Machine')
[System.Environment]::SetEnvironmentVariable('GROQ_API_KEY', 'your-groq-key-here', 'Machine')

# Verify
[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'Machine')
```

#### Option B: User Environment Variables
```powershell
# For current user only
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-key-here', 'User')
```

#### Option C: Using .env file (DEPRECATED - DO NOT USE)
```bash
# ❌ DO NOT CREATE THIS FILE - Use environment variables instead
# .env files can be accidentally committed to version control
```

### Step 2: Verify Environment Variables

```powershell
# Test that environment variables are set correctly
$env:OPENAI_API_KEY
$env:CASCAD_API_KEY
$env:ANTHROPIC_API_KEY

# If not set, check system variables
[System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'Machine')
[System.Environment]::GetEnvironmentVariable('CASCAD_API_KEY', 'Machine')
```

### Step 3: Test API Key Functionality

```python
# Run this Python test
import os
import sys
sys.path.insert(0, '.')

# Check environment variables
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)})")
    # Test basic OpenAI client initialization
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ OpenAI client failed: {e}")
else:
    print("❌ OPENAI_API_KEY not found in environment variables")
```

## 🔍 MONITORING FOR CASCADE ERRORS

### Watch for These Error Patterns:

#### 1. API Key Related Errors:
```
AuthenticationError: Incorrect API key provided
APIConnectionError: Connection error
RateLimitError: Rate limit exceeded
```

#### 2. Missing Key Errors:
```
openai.AuthenticationError: No API key provided
ValueError: Must provide an API key
```

#### 3. Cascade Agent Errors:
```
Error acknowledging Cascade edit: ConnectError
no unacknowledged steps for file
```

### Monitoring Commands:

```powershell
# Check environment variables
Get-ChildItem Env: | Where-Object { $_.Name -match "API|KEY|SECRET" }

# Monitor Windsurf logs for errors
# Open: %APPDATA%\Windsurf\logs\renderer.log
# Look for: "Error acknowledging Cascade edit" or "API key" errors
```

## 🛠️ TROUBLESHOOTING CASCADE ISSUES

### If Cascade Errors Persist:

#### Step 1: Verify API Keys
```python
import os
print("API Keys Status:")
print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
print(f"CASCAD_API_KEY: {'✅ Set' if os.getenv('CASCAD_API_KEY') else '❌ Missing'}")
print(f"ANTHROPIC_API_KEY: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
```

#### Step 2: Test API Connectivity
```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.models.list()
    print("✅ API connectivity working")
except Exception as e:
    print(f"❌ API connectivity failed: {e}")
```

#### Step 3: Clear Windsurf Cache
```powershell
# Stop Windsurf completely
Stop-Process -Name "Windsurf" -Force -ErrorAction SilentlyContinue

# Clear cache (adjust path as needed)
Remove-Item -Path "$env:APPDATA\Windsurf\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\Windsurf\Code Cache\*" -Recurse -Force -ErrorAction SilentlyContinue

# Restart Windsurf
Start-Process "C:\Users\$env:USERNAME\AppData\Local\Programs\Windsurf\Windsurf.exe"
```

## 🚨 EMERGENCY: REINSTALL WINDSURF

### If All Else Fails:

#### Complete Reinstall Process:
```powershell
# Step 1: Backup your settings (optional)
# Copy important VS Code settings to backup location

# Step 2: Complete Uninstall
winget uninstall --id Windsurf.Windsurf
# OR manually uninstall from Control Panel

# Step 3: Clean Registry (Advanced Users Only)
# Use CCleaner or manually clean registry keys:
# HKEY_CURRENT_USER\Software\Windsurf

# Step 4: Clean AppData
Remove-Item -Path "$env:APPDATA\Windsurf" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Programs\Windsurf" -Recurse -Force -ErrorAction SilentlyContinue

# Step 5: Reinstall
winget install --id Windsurf.Windsurf

# Step 6: Restore Environment Variables
# Re-run the environment variable setup commands above

# Step 7: Test
# Restart development environment and test Cascade functionality
```

## ✅ VERIFICATION CHECKLIST

- [ ] All .env and key files deleted
- [ ] Environment variables set correctly (OPENAI_API_KEY, CASCAD_API_KEY)
- [ ] API keys accessible to Python processes
- [ ] OpenAI client initializes without errors
- [ ] Cascade extension loads without acknowledgment errors
- [ ] Tool executions complete successfully

## 🔒 SECURITY NOTES

1. **Never commit API keys to version control**
2. **Use environment variables, not files**
3. **Rotate keys regularly**
4. **Monitor for unauthorized access**
5. **Use separate keys for different environments**

---
**Status: 🔐 SECURE API KEY SETUP COMPLETE**
**Next: Monitor Cascade agent for errors and test functionality**
