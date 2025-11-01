# Cascade API Key Setup and Verification Script
# Run this script as Administrator in PowerShell

Write-Host "🚀 Cascade API Key Setup Script" -ForegroundColor Green
Write-Host "=" * 35 -ForegroundColor Green
Write-Host ""

# Step 1: Set environment variable
Write-Host "Step 1: Setting CASCAD_API_KEY environment variable..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable('CASCAD_API_KEY', 'sk-ws-01-San-LQfCjNs-V2WokDFnzSXQftsn5MDQESIh_IucWyeIIHblAXy0YPHfBomv7_SfAN9S5D8PMKsqfuVatXMAVrEhiNdimA', 'Machine')

# Step 2: Verify environment variable
Write-Host ""
Write-Host "Step 2: Verifying environment variable..." -ForegroundColor Yellow
$cascadeKey = [System.Environment]::GetEnvironmentVariable('CASCAD_API_KEY', 'Machine')
if ($cascadeKey) {
    $masked = $cascadeKey.Substring(0, [Math]::Min(12, $cascadeKey.Length)) + "..." + $cascadeKey.Substring([Math]::Max(0, $cascadeKey.Length - 4))
    Write-Host "✅ CASCAD_API_KEY: $masked (length: $($cascadeKey.Length))" -ForegroundColor Green
} else {
    Write-Host "❌ CASCAD_API_KEY: Not found" -ForegroundColor Red
}

# Step 3: Check OpenAI key
Write-Host ""
Write-Host "Step 3: Checking OpenAI API key..." -ForegroundColor Yellow
$openaiKey = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'Machine')
if ($openaiKey) {
    $masked = $openaiKey.Substring(0, [Math]::Min(12, $openaiKey.Length)) + "..." + $openaiKey.Substring([Math]::Max(0, $openaiKey.Length - 4))
    Write-Host "✅ OPENAI_API_KEY: $masked (length: $($openaiKey.Length))" -ForegroundColor Green
} else {
    Write-Host "⚠️  OPENAI_API_KEY: Not found (optional)" -ForegroundColor Yellow
}

# Step 4: Test Python functionality
Write-Host ""
Write-Host "Step 4: Testing Python environment..." -ForegroundColor Yellow
try {
    # Change to project directory
    Set-Location "E:\Projects\Echoes"

    # Run Python test
    python -c "
import os
print('🔍 Python Environment Test:')
print('=' * 28)
try:
    import sys
    sys.path.insert(0, '.')
    from assistant_v2_core import EchoesAssistantV2
    print('✅ Assistant import successful')
except Exception as e:
    print(f'❌ Import failed: {str(e)[:50]}...')

try:
    cascade_key = os.getenv('CASCAD_API_KEY')
    print(f'✅ CASCAD_API_KEY accessible: {bool(cascade_key)}')
except:
    print('❌ Environment variable not accessible')
"
} catch {
    Write-Host "❌ Python test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Restart Windsurf IDE completely" -ForegroundColor White
Write-Host "2. Clear Windsurf cache if needed (see CASCADE_ERROR_TROUBLESHOOTING.md)" -ForegroundColor White
Write-Host "3. Test Cascade edit functionality" -ForegroundColor White
Write-Host "4. Monitor for acknowledgment errors" -ForegroundColor White

Write-Host ""
Write-Host "🎉 Setup complete! Press Enter to exit..." -ForegroundColor Green
Read-Host
