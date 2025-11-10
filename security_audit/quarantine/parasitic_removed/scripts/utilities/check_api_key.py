#!/usr/bin/env python3
"""
Secure API Key Verification - Tests OpenAI API access without storing credentials
"""

import os
import sys


def check_api_key():
    """Check if API key is properly configured via environment variables"""
    print("🔐 SECURE API KEY VERIFICATION")
    print("=" * 50)
    print("This script verifies OpenAI API key access from environment variables.")
    print("No credentials are stored or logged - maximum security approach.\n")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("\n🔑 To set securely (choose one method):")
        print("\n  PowerShell (temporary session):")
        print("    $env:OPENAI_API_KEY='sk-your-key-here'")
        print("\n  PowerShell (permanent - User level):")
        print(
            "    [Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')"
        )
        print("\n  CMD (temporary session):")
        print("    set OPENAI_API_KEY=sk-your-key-here")
        print("\n  CMD (permanent - System level):")
        print("    setx OPENAI_API_KEY sk-your-key-here")
        print("\n  Linux/Mac:")
        print("    export OPENAI_API_KEY=sk-your-key-here")
        print("    # Add to ~/.bashrc or ~/.zshrc for permanence")
        return False

    if api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY is set to placeholder value")
        print("Please set it to your actual OpenAI API key")
        return False

    # Check if it looks like a real API key (starts with sk-)
    if not api_key.startswith("sk-"):
        print("⚠️  OPENAI_API_KEY doesn't look like a valid OpenAI key")
        print("   OpenAI API keys should start with 'sk-'")
        print(f"   Your key starts with: {api_key[:4]}...")
        return False

    print("✅ OPENAI_API_KEY environment variable found")
    print(f"   Key format: sk-{'*' * 20}{api_key[-4:] if len(api_key) > 24 else ''}")
    print(f"   Length: {len(api_key)} characters ✓")

    # Test OpenAI client initialization (no API call)
    try:
        import openai

        openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        print("   Ready for API calls without storing credentials")

        # Optional: Test a minimal API call (commented out for security)
        print("\n🧪 Optional API Test (uncomment in check_api_key.py if desired):")
        print("   # Test actual API connectivity")
        print("   # response = client.chat.completions.create(...)")
        print("   # This would make a real API call and incur costs")

        return True

    except Exception as e:
        print(f"❌ OpenAI client initialization failed: {e}")
        print("   Check that your API key is valid and has proper permissions")
        return False


def test_minimal_api_call():
    """Optional: Test actual API connectivity (uncomment if desired)"""
    print("\n🧪 Testing actual API connectivity...")
    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ No API key found")
            return False

        client = openai.OpenAI(api_key=api_key)
        # Minimal test call - very low cost
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
        )
        print("✅ API connectivity confirmed")
        print(f"   Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False


if __name__ == "__main__":
    success = check_api_key()

    if success:
        print("\n🎉 API Key Verification Complete!")
        print("Your OpenAI API key is properly configured via environment variables.")
        print(
            "The Echoes system can now make secure API calls without storing credentials."
        )

        # Uncomment the line below if you want to test actual API connectivity
        # test_minimal_api_call()

    sys.exit(0 if success else 1)
