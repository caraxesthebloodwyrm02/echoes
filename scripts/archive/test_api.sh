#!/bin/bash
# API Functionality Test Script

echo '🚀 Testing FastAPI Application...'
echo '================================'

# Test 1: Health check
echo '1. Testing health endpoint...'
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo '   ✅ Health check passed'
else
    echo '   ❌ Health check failed'
    exit 1
fi

# Test 2: OpenAPI schema
echo '2. Testing OpenAPI schema...'
if curl -f http://localhost:8000/openapi.json > /dev/null 2>&1; then
    echo '   ✅ OpenAPI schema accessible'
else
    echo '   ❌ OpenAPI schema not accessible'
    exit 1
fi

# Test 3: API documentation
echo '3. Testing API documentation...'
if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo '   ✅ API documentation accessible'
else
    echo '   ❌ API documentation not accessible'
    exit 1
fi

# Test 4: Authentication endpoint
echo '4. Testing authentication endpoint...'
AUTH_RESPONSE=

if echo \
\ | grep -q 'access_token'; then
    echo '   ✅ Authentication working'
    TOKEN=
    echo '   📝 Token received'
else
    echo '   ⚠️ Authentication may need configuration'
fi

# Test 5: Protected endpoint (if token available)
if [ ! -z \\ ]; then
    echo '5. Testing protected endpoint...'
    PROTECTED_RESPONSE=
    if echo \\ | grep -q 'username'; then
        echo '   ✅ Protected endpoint working'
    else
        echo '   ❌ Protected endpoint failed'
    fi
fi

echo ''
echo '🎉 All tests completed!'
echo '📖 API Documentation: http://localhost:8000/docs'
echo '🔍 OpenAPI Schema: http://localhost:8000/openapi.json'
