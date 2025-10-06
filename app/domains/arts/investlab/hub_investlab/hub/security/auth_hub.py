#!/usr/bin/env python3
"""
Authentication Hub - Web-based OAuth2 login for Google, Microsoft, and X
"""

import os
import sys
from datetime import datetime
from auth.web_app import create_auth_app
from auth.user_manager import UserManager
from auth.oauth_manager import OAuthManager

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("    AUTHENTICATION HUB v1.0")
    print("    Web-based OAuth2 Login System")
    print("    Google - Microsoft - X (Twitter)")
    print("=" * 70)

def check_configuration():
    """Check OAuth configuration"""
    oauth = OAuthManager()
    
    configured = []
    not_configured = []
    
    for provider in ['google', 'microsoft', 'twitter']:
        if oauth.is_configured(provider):
            configured.append(provider.title())
        else:
            not_configured.append(provider.title())
    
    print("\nConfiguration Status:")
    if configured:
        print(f"  ✅ Configured: {', '.join(configured)}")
    if not_configured:
        print(f"  ⚠️  Not configured: {', '.join(not_configured)}")
        print("    Add client credentials to .env file")
    
    return len(configured) > 0

def create_sample_env():
    """Create sample .env file if it doesn't exist"""
    env_file = '.env'
    if not os.path.exists(env_file):
        sample_env = """# Authentication Hub Configuration

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this

# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Microsoft OAuth2
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret

# Twitter/X OAuth2
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret

# Web App Settings
PORT=5001
DEBUG=False
"""
        with open(env_file, 'w') as f:
            f.write(sample_env)
        print(f"  📄 Created {env_file} - please configure your OAuth credentials")
        return True
    return False

def main():
    """Main function"""
    print_banner()
    
    # Create sample .env if needed
    env_created = create_sample_env()
    
    # Check configuration
    has_configured = check_configuration()
    
    if not has_configured and not env_created:
        print("\n❌ No OAuth providers configured.")
        print("   Please set up OAuth credentials in .env file")
        return
    
    # Create and run the authentication app
    app = create_auth_app()
    
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"\n🚀 Starting Authentication Hub...")
    print(f"   Web interface: http://localhost:{port}")
    print(f"   Login page: http://localhost:{port}/")
    print(f"   Press Ctrl+C to stop")
    
    try:
        app.run(port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Authentication Hub stopped")

if __name__ == "__main__":
    main()
