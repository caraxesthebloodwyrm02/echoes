#!/usr/bin/env python3
"""
Twitter Credentials Verification
Automatically checks Twitter API credentials from environment variables
"""

import os
import sys


def check_twitter_credentials():
    """Check if Twitter API credentials are available in environment variables."""

    print(" Twitter API Credentials Check")
    print("=" * 50)

    # Check for Bearer Token (Twitter API v2)
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if bearer_token:
        print(" TWITTER_BEARER_TOKEN: Set")
        print(f"   Length: {len(bearer_token)} characters")
        print(f"   Starts with: {bearer_token[:10]}...")
        # Don't print the full token for security
    else:
        print(" TWITTER_BEARER_TOKEN: Not set")

    # Check for OAuth 1.0a credentials (Twitter API v1.1)
    oauth_vars = {
        "TWITTER_API_KEY": os.getenv("TWITTER_API_KEY"),
        "TWITTER_API_SECRET": os.getenv("TWITTER_API_SECRET"),
        "TWITTER_ACCESS_TOKEN": os.getenv("TWITTER_ACCESS_TOKEN"),
        "TWITTER_ACCESS_TOKEN_SECRET": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    }

    oauth_set = all(oauth_vars.values())
    if oauth_set:
        print(" OAuth 1.0a credentials: All set")
        for var_name in oauth_vars:
            value = oauth_vars[var_name]
            if value:
                print(f"   {var_name}: Set (starts with {value[:8]}...)")
    else:
        print(" OAuth 1.0a credentials: Incomplete")
        for var_name, value in oauth_vars.items():
            status = "Set" if value else "Not set"
            print(f"   {var_name}: {status}")

    print()

    # Determine which authentication method to use
    if bearer_token:
        print(" Using: Twitter API v2 (Bearer Token)")
        return "bearer"
    elif oauth_set:
        print(" Using: Twitter API v1.1 (OAuth 1.0a)")
        return "oauth"
    else:
        print(" No valid Twitter API credentials found!")
        print()
        print("To set up credentials:")
        print("1. Run: python setup_twitter_auto.py")
        print("2. Enter your credentials when prompted")
        print("3. Or set environment variables manually:")
        print("   # For API v2 (recommended):")
        print("   set TWITTER_BEARER_TOKEN=your_bearer_token_here")
        print("   ")
        print("   # OR for API v1.1:")
        print("   set TWITTER_API_KEY=your_api_key")
        print("   set TWITTER_API_SECRET=your_api_secret")
        print("   set TWITTER_ACCESS_TOKEN=your_access_token")
        print("   set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret")
        return None


def test_authentication():
    """Test authentication with the available credentials"""
    auth_method = check_twitter_credentials()
    if not auth_method:
        return False

    print("\n Testing Authentication...")
    print("=" * 30)

    try:
        # Import and test the monitor
        sys.path.insert(0, ".")
        from app.social_monitoring import TwitterMonitor

        # Initialize Twitter monitor (will auto-load from env vars)
        twitter = TwitterMonitor()

        # Test authentication
        if twitter.authenticate():
            print(" Authentication successful!")
            print(f"   Method: {auth_method.upper()}")

            # Test a simple API call
            print("\n Testing API functionality...")
            try:
                # Try to get trending topics (lightweight test)
                trends = twitter.get_trending_topics(woeid=1)  # Worldwide
                if trends:
                    print(f" API working! Found {len(trends)} trending topics")
                    print(f"   Sample: {trends[0]['name'] if trends else 'None'}")
                else:
                    print(" API responded but no trends returned")
            except Exception as e:
                print(f" API test failed: {e}")

            return True
        else:
            print(" Authentication failed!")
            print("   Check your credentials are correct and API access is enabled")
            return False

    except ImportError as e:
        print(f" Import error: {e}")
        print("   Make sure the app.social_monitoring module is available")
        return False
    except Exception as e:
        print(f" Error during authentication test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_authentication()
    if success:
        print("\n Twitter credentials are working!")
        print("You can now run: python demo_twitter_search.py")
    else:
        print("\n Twitter credentials need to be set up.")
        print("Run: python setup_twitter_auto.py")
