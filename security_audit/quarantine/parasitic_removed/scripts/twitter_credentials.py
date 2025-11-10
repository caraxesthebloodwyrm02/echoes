# twitter_credentials.py
import os

CREDENTIAL_FIELDS = {
    "bearer_token": ("TWITTER_BEARER_TOKEN", "Bearer token (API v2)"),
    "api_key": ("TWITTER_API_KEY", "API key (consumer key)"),
    "api_secret": ("TWITTER_API_SECRET", "API secret (consumer secret)"),
    "access_token": ("TWITTER_ACCESS_TOKEN", "Access token"),
    "access_token_secret": ("TWITTER_ACCESS_TOKEN_SECRET", "Access token secret"),
}


def _mask_secret(value: str | None) -> str:
    """Return a masked representation of a secret value."""
    if not value:
        return "not set"

    trimmed = value.strip()
    return f"{trimmed[:4]}…{trimmed[-2:]} (len={len(trimmed)})"


def get_twitter_credentials() -> dict[str, str | None]:
    """Retrieve Twitter API credentials from environment variables.

    Returns:
        Dict containing Twitter API credentials with the following keys:
        - bearer_token: For Twitter API v2
        - api_key: Twitter API Key
        - api_secret: Twitter API Secret
        - access_token: Twitter Access Token
        - access_token_secret: Twitter Access Token Secret
    """
    return {
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
        "api_key": os.getenv("TWITTER_API_KEY"),
        "api_secret": os.getenv("TWITTER_API_SECRET"),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    }


def check_credentials(creds: dict[str, str | None]) -> bool:
    """Check if valid Twitter API credentials are available.

    Args:
        creds: Dictionary of credentials from get_twitter_credentials()

    Returns:
        bool: True if either Bearer Token or complete OAuth 1.0a credentials are available
    """
    # Check for Bearer Token (API v2)
    if creds.get("bearer_token"):
        return True

    # Check for complete OAuth 1.0a credentials (API v1.1)
    oauth_creds = [
        creds.get("api_key"),
        creds.get("api_secret"),
        creds.get("access_token"),
        creds.get("access_token_secret"),
    ]
    return all(oauth_creds)


if __name__ == "__main__":
    """Command-line interface to verify Twitter credentials."""
    creds = get_twitter_credentials()
    print("🔍 Twitter API Credentials Check")
    print("=" * 50)

    if check_credentials(creds):
        auth_method = "Bearer Token" if creds.get("bearer_token") else "OAuth 1.0a"
        print(f"✅ Valid credentials found! Using: {auth_method}")
        print("\nCredential summary (masked):")
        for key, (env_var, label) in CREDENTIAL_FIELDS.items():
            masked = _mask_secret(creds.get(key))
            print(f"   • {label}: {masked}")
    else:
        print("❌ No valid Twitter API credentials found in environment variables!")
        print("\nPlease set your Twitter API credentials in environment variables:")
        print("\nFor API v2 (recommended):")
        print("   set TWITTER_BEARER_TOKEN=your_bearer_token_here")
        print("\nOR for API v1.1:")
        print("   set TWITTER_API_KEY=your_api_key")
        print("   set TWITTER_API_SECRET=your_api_secret")
        print("   set TWITTER_ACCESS_TOKEN=your_access_token")
        print("   set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret")
        print("\nNote: Environment variables are preferred over hardcoded credentials.")
