@echo off
REM Cascade API Key Setup and Verification Script
REM Run this as Administrator

echo 🚀 Cascade API Key Setup Script
echo =================================
echo.

echo Step 1: Setting CASCAD_API_KEY environment variable...
powershell -Command "[System.Environment]::SetEnvironmentVariable('CASCAD_API_KEY', 'sk-ws-01-San-LQfCjNs-V2WokDFnzSXQftsn5MDQESIh_IucWyeIIHblAXy0YPHfBomv7_SfAN9S5D8PMKsqfuVatXMAVrEhiNdimA', 'Machine')"

echo.
echo Step 2: Verifying environment variable...
powershell -Command "[System.Environment]::GetEnvironmentVariable('CASCAD_API_KEY', 'Machine')"

echo.
echo Step 3: Testing Python environment...
cd E:\Projects\Echoes
python -c "
import os
print('🔍 Environment Variable Check:')
print('=' * 35)
cascade_key = os.getenv('CASCAD_API_KEY')
if cascade_key:
    masked = cascade_key[:12] + '...' + cascade_key[-4:] if len(cascade_key) > 16 else '****'
    print(f'✅ CASCAD_API_KEY: {masked} (length: {len(cascade_key)})')
else:
    print('❌ CASCAD_API_KEY: Not found')

openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    masked = openai_key[:12] + '...' + openai_key[-4:] if len(openai_key) > 16 else '****'
    print(f'✅ OPENAI_API_KEY: {masked} (length: {len(openai_key)})')
else:
    print('⚠️  OPENAI_API_KEY: Not found (optional)')

print()
print('📋 Next Steps:')
print('1. Restart Windsurf IDE completely')
print('2. Clear Windsurf cache if needed')
print('3. Test Cascade edit functionality')
print('4. Monitor for acknowledgment errors')
"

echo.
echo 🎉 Setup complete! Press any key to exit...
pause > nul
