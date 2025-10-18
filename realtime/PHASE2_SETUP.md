# Phase 2 Setup Guide

## Prerequisites

Python 3.8+ is required for Phase 2 authentication features.

## Installation

### Step 1: Install Phase 2 Dependencies

```bash
pip install -r requirements-phase2.txt
```

Or install individually:

```bash
pip install PyJWT>=2.8.0
pip install pytest>=7.4.0
pip install fastapi>=0.104.0
pip install uvicorn>=0.24.0
```

### Step 2: Verify Installation

Run the quick authentication test:

```bash
python quick_auth_test.py
```

Expected output:
```
======================================================================
AUTHENTICATION SYSTEM - QUICK TEST
======================================================================

[1/5] Testing JWT Token Handler...
✅ JWT Handler: PASSED

[2/5] Testing API Key Manager...
✅ API Key Manager: PASSED

[3/5] Testing Permissions...
✅ Permissions: PASSED

[4/5] Testing Rate Limiter...
✅ Rate Limiter: PASSED

[5/5] Testing Complete Workflow...
✅ Integration Workflow: PASSED

======================================================================
✅ ALL TESTS PASSED - Authentication System Operational!
======================================================================
```

### Step 3: Run Full Test Suite (Optional)

If pytest is installed:

```bash
pytest tests/test_auth_system.py -v
```

## Configuration

### Environment Variables

Create a `.env` file with:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Generate API Keys

```python
from api.auth.api_keys import APIKeyManager

manager = APIKeyManager()

# Generate admin key
admin_key = manager.generate_key(
    name="Admin User",
    role="admin",
    platforms=["echoes", "turbo", "glimpse"]
)
print(f"Admin API Key: {admin_key}")

# Generate researcher key
researcher_key = manager.generate_key(
    name="Research Team",
    role="researcher",
    platforms=["glimpse", "turbo"]
)
print(f"Researcher API Key: {researcher_key}")
```

**⚠️ Important**: Store API keys securely! They cannot be recovered once lost.

## Usage Examples

### 1. JWT Authentication

```python
from api.auth.jwt_handler import create_access_token, verify_token

# Create token
token = create_access_token({
    "sub": "user123",
    "role": "researcher",
    "platforms": ["glimpse", "turbo"]
})

# Verify token
payload = verify_token(token)
print(f"User: {payload['sub']}, Role: {payload['role']}")
```

### 2. API Key Validation

```python
from api.auth.api_keys import APIKeyManager

manager = APIKeyManager()

# Validate incoming API key
key_data = manager.validate_key(api_key_from_request)
if key_data:
    print(f"Valid key: {key_data['name']}")
    print(f"Role: {key_data['role']}")
else:
    print("Invalid or revoked key")
```

### 3. Permission Checking

```python
from api.auth.permissions import has_permission, can_access_platform, Roles

# Check role hierarchy
if has_permission(user_role, Roles.ADMIN):
    print("User has admin privileges")

# Check platform access
if can_access_platform(user_role, "glimpse"):
    print("User can access Glimpse platform")
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'jwt'"

**Solution**: Install PyJWT
```bash
pip install PyJWT
```

### Issue: "Permission denied" when creating API keys

**Solution**: Ensure write permissions in the current directory or specify a custom path:
```python
manager = APIKeyManager(storage_path="/path/to/writable/location/keys.json")
```

### Issue: Rate limiter not working

**Solution**: Ensure middleware is added to FastAPI app:
```python
from fastapi import FastAPI
from api.middleware.rate_limiter import RateLimiter

app = FastAPI()
app.add_middleware(RateLimiter, requests_per_minute=60)
```

## Next Steps

Once authentication is verified:

1. **Week 2**: Implement monitoring and logging
2. **Week 3**: Set up production deployment
3. **Week 4**: Add extended integrations (WebSocket, batch processing)

See `PHASE2_PLAN.md` for complete roadmap.
