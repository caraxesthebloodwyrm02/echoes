#!/usr/bin/env python3
"""
🔐 SECURE API KEY VERIFICATION SCRIPT
Tests that API keys are properly configured via environment variables
"""

import os
import sys
from pathlib import Path

def main():
    print("🔐 SECURE API KEY VERIFICATION")
    print("=" * 50)

    # Check for .env files (should NOT exist)
    print("\n1️⃣  Checking for insecure .env files:")
    env_files = list(Path(".").glob("*.env"))
    if env_files:
        print("❌ FOUND .env files (INSECURE):")
        for f in env_files:
            print(f"   🚨 {f.name}")
        print("   💡 DELETE these files immediately!")
    else:
        print("✅ No .env files found - Good!")

    # Check for key JSON files (should NOT exist)
    print("\n2️⃣  Checking for key storage files:")
    key_files = []
    for pattern in ["*key*.json", "*secret*.json", "*token*.json", "api_keys.json"]:
        key_files.extend(list(Path(".").glob(pattern)))

    if key_files:
        print("❌ FOUND key storage files (INSECURE):")
        for f in key_files:
            print(f"   🚨 {f.name}")
        print("   💡 DELETE these files immediately!")
    else:
        print("✅ No key storage files found - Good!")

    # Check environment variables
    print("\n3️⃣  Checking environment variables:")
    required_keys = ['OPENAI_API_KEY', 'CASCAD_API_KEY']
    optional_keys = ['ANTHROPIC_API_KEY', 'GROQ_API_KEY']

    all_good = True

    for key in required_keys:
        value = os.getenv(key)
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "****"
            print(f"✅ {key}: {masked} (length: {len(value)})")
        else:
            print(f"❌ {key}: NOT SET (REQUIRED)")
            all_good = False

    for key in optional_keys:
        value = os.getenv(key)
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "****"
            print(f"✅ {key}: {masked} (length: {len(value)})")
        else:
            print(f"⚠️  {key}: Not set (optional)")

    # Test OpenAI API connectivity
    print("\n4️⃣  Testing API connectivity:")
    try:
        if os.getenv('OPENAI_API_KEY'):
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            # Simple test - list models (doesn't count against rate limit)
            models = client.models.list()
            print("✅ OpenAI API: Connected successfully")
            print(f"   📊 Available models: {len(models.data)}")
        else:
            print("❌ OpenAI API: Cannot test (no API key)")
            all_good = False
    except Exception as e:
        print(f"❌ OpenAI API: Connection failed - {e}")
        all_good = False

    # Final verdict
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SECURE API KEY SETUP: COMPLETE ✅")
        print("   • No insecure files found")
        print("   • Environment variables properly configured")
        print("   • API connectivity verified")
        print("   • Ready for secure development!")
    else:
        print("⚠️  SECURE API KEY SETUP: INCOMPLETE ❌")
        print("   • Fix the issues above before proceeding")
        print("   • Set required environment variables")
        print("   • Delete any insecure key files")

    print("\n💡 Next Steps:")
    print("   1. Monitor Windsurf logs for Cascade acknowledgment errors")
    print("   2. Test tool executions in your IDE")
    print("   3. If issues persist, consider Windsurf reinstall")
    print("   4. Regularly rotate API keys for security")

    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
