#!/usr/bin/env python3
"""
Automated Twitter Credentials Setup
Extracts credentials from user input or environment and sets them up automatically
"""

import json
import os
import sys
from pathlib import Path


def extract_credentials_from_screenshot():
    """
    Extract Twitter API credentials from screenshot or user input
    Since I can't read screenshots directly, this function prompts for manual entry
    """
    print("🔍 Twitter Credentials Setup")
    print("=" * 50)

    print("\n📸 Please provide your Twitter API credentials:")
    print("   (Copy them from your Twitter Developer Portal)")

    # Bearer Token (API v2)
    bearer_token = input("\nEnter your Bearer Token: ").strip()
    if not bearer_token:
        print("❌ Bearer Token is required!")
        return None

    # Optional OAuth 1.0a credentials
    print(
        "\n📝 Optional OAuth 1.0a credentials (leave blank if using Bearer Token only):"
    )

    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    access_token = input("Access Token: ").strip()
    access_token_secret = input("Access Token Secret: ").strip()

    credentials = {
        "bearer_token": bearer_token,
        "api_key": api_key or None,
        "api_secret": api_secret or None,
        "access_token": access_token or None,
        "access_token_secret": access_token_secret or None,
    }

    return credentials


def set_environment_variables(credentials):
    """Set environment variables for Twitter credentials"""
    print("\n🔧 Setting environment variables...")

    # Set the Bearer Token (required)
    os.environ["TWITTER_BEARER_TOKEN"] = credentials["bearer_token"]
    print("✅ TWITTER_BEARER_TOKEN set")

    # Set optional OAuth credentials
    if credentials["api_key"]:
        os.environ["TWITTER_API_KEY"] = credentials["api_key"]
        print("✅ TWITTER_API_KEY set")

    if credentials["api_secret"]:
        os.environ["TWITTER_API_SECRET"] = credentials["api_secret"]
        print("✅ TWITTER_API_SECRET set")

    if credentials["access_token"]:
        os.environ["TWITTER_ACCESS_TOKEN"] = credentials["access_token"]
        print("✅ TWITTER_ACCESS_TOKEN set")

    if credentials["access_token_secret"]:
        os.environ["TWITTER_ACCESS_TOKEN_SECRET"] = credentials["access_token_secret"]
        print("✅ TWITTER_ACCESS_TOKEN_SECRET set")

    return True


def create_credentials_file(credentials, filename="twitter_credentials.json"):
    """Create a secure credentials file for backup"""
    try:
        # Don't save full credentials for security - just metadata
        metadata = {
            "bearer_token_set": bool(credentials["bearer_token"]),
            "oauth_credentials_set": bool(
                credentials["api_key"] and credentials["api_secret"]
            ),
            "created_at": str(Path(filename).stat().st_mtime)
            if Path(filename).exists()
            else None,
            "note": "Actual credentials stored in environment variables only",
        }

        with open(filename, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Credentials metadata saved to {filename}")
        return True

    except Exception as e:
        print(f"⚠️ Could not create credentials file: {e}")
        return False


def test_credentials():
    """Test that credentials are working"""
    print("\n🧪 Testing credentials...")

    try:
        # Import and test the monitor
        sys.path.insert(0, ".")
        from app.social_monitoring import TwitterMonitor

        # Initialize with environment variables
        twitter = TwitterMonitor()

        # Test authentication
        if twitter.authenticate():
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed!")
            return False

    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Automated Twitter Credentials Setup")
    print("=" * 50)

    # Get credentials
    credentials = extract_credentials_from_screenshot()
    if not credentials:
        return

    # Set environment variables
    if not set_environment_variables(credentials):
        return

    # Create metadata file
    create_credentials_file(credentials)

    # Test credentials
    if test_credentials():
        print("\n🎉 Setup complete! You can now run:")
        print("   python check_twitter_credentials.py")
        print("   python demo_twitter_search.py")
    else:
        print("\n❌ Setup completed but credentials test failed.")
        print("Please verify your credentials are correct.")


if __name__ == "__main__":
    main()
