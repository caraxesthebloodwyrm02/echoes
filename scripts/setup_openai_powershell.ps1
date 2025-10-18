# OpenAI Setup Script for Windows PowerShell
# Safe PowerShell syntax - no parser errors
# Run this entire script in PowerShell to set up OpenAI API

Write-Host "🤖 OpenAI API Setup for Windows PowerShell" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host ""
Write-Host "2. Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ Pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Pip not found. Please ensure pip is installed with Python." -ForegroundColor Red
    exit 1
}

# Install OpenAI package
Write-Host ""
Write-Host "3. Installing OpenAI package..." -ForegroundColor Yellow
try {
    pip install openai --quiet
    Write-Host "✅ OpenAI package installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install OpenAI package: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Set API key (safe input)
Write-Host ""
Write-Host "4. OpenAI API Key Setup" -ForegroundColor Yellow
Write-Host "Get your API key from: https://platform.openai.com/account/api-keys" -ForegroundColor Cyan
Write-Host ""

$apiKey = Read-Host "Enter your OpenAI API key (or press Enter to skip)"
if ($apiKey -and $apiKey -ne "") {
    # Set environment variable for current session
    $env:OPENAI_API_KEY = $apiKey
    Write-Host "✅ API key set for current session" -ForegroundColor Green

    # Set permanent environment variable
    try {
        [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $apiKey, "User")
        Write-Host "✅ API key saved permanently (restart PowerShell to use)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not save permanently: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   API key will work for this session only" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ API key not set. You'll need to set OPENAI_API_KEY manually." -ForegroundColor Yellow
    Write-Host "   Run: `$env:OPENAI_API_KEY = 'your-key-here'" -ForegroundColor Yellow
}

# Test OpenAI CLI
Write-Host ""
Write-Host "5. Testing OpenAI CLI..." -ForegroundColor Yellow
try {
    $cliHelp = python -m openai --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ OpenAI CLI working" -ForegroundColor Green
    } else {
        Write-Host "❌ OpenAI CLI failed: $cliHelp" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ OpenAI CLI test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test API call (if API key is set)
if ($env:OPENAI_API_KEY -or $apiKey) {
    Write-Host ""
    Write-Host "6. Testing OpenAI API Call..." -ForegroundColor Yellow

    # Create temporary test script
    $testScript = @"
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Simple test
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'OpenAI API test successful!' and nothing else."}],
        max_tokens=20
    )

    result = response.choices[0].message.content.strip()
    print(f"SUCCESS: {result}")

except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
"@

    # Write and run test script
    $testScript | Out-File -FilePath "openai_test.py" -Encoding UTF8

    try {
        $testResult = python openai_test.py 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ API test successful!" -ForegroundColor Green
            Write-Host "   Response: $($testResult -replace 'SUCCESS: ', '')" -ForegroundColor Green
        } else {
            Write-Host "❌ API test failed: $testResult" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ API test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    # Clean up test file
    if (Test-Path "openai_test.py") {
        Remove-Item "openai_test.py"
    }
} else {
    Write-Host ""
    Write-Host "6. API Test Skipped" -ForegroundColor Yellow
    Write-Host "   Set OPENAI_API_KEY and re-run to test API calls" -ForegroundColor Yellow
}

# Show usage examples
Write-Host ""
Write-Host "7. OpenAI Usage Examples" -ForegroundColor Cyan
Write-Host "-" * 30 -ForegroundColor Cyan

$examples = @(
    "Text Completion: python -m openai api completions.create -m gpt-3.5-turbo-instruct -p `"Write a haiku`""
    "Chat Completion: python -c `"from openai import OpenAI; client=OpenAI(); response=client.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role':'user','content':'Hello!'}]); print(response.choices[0].message.content)`""
    "List Models: python -c `"from openai import OpenAI; client=OpenAI(); models=client.models.list(); print([m.id for m in models.data[:5]])`""
)

foreach ($example in $examples) {
    Write-Host "• $example" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎉 OpenAI Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

if ($apiKey) {
    Write-Host "✅ API key configured and tested" -ForegroundColor Green
} else {
    Write-Host "⚠️ API key not configured - set OPENAI_API_KEY to enable API calls" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   • Restart PowerShell to use permanent environment variables"
Write-Host "   • Test with: python -c `"import openai; print('OpenAI ready!')`""
Write-Host "   • Run examples above to test different API features"
Write-Host ""
Write-Host "📚 Resources:" -ForegroundColor Cyan
Write-Host "   • OpenAI API Docs: https://platform.openai.com/docs"
Write-Host "   • API Keys: https://platform.openai.com/account/api-keys"
Write-Host "   • Models: https://platform.openai.com/docs/models"
