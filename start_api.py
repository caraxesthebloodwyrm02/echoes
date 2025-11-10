#!/usr/bin/env python3
"""
Echoes API Startup Script

This script provides a convenient way to start the Echoes research API
with proper configuration and environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment")
        return False

    return True


def create_env_template():
    """Create .env template if it doesn't exist"""
    env_template = Path(".env")

    if not env_template.exists():
        template_content = """# Echoes API Environment Configuration

# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_RELOAD=true

# Logging
LOG_LEVEL=INFO

# Glimpse Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_CACHE_DIR=.cache/embeddings
RETRIEVAL_INDEX_TYPE=flat
RETRIEVAL_METRIC=cosine
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Security (Optional)
API_KEY_REQUIRED=false
ALLOWED_API_KEYS=[]
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# CORS
CORS_ORIGINS=["*"]
"""
        env_template.write_text(template_content)
        print("✅ Created .env template file")
        print("   Please edit .env and add your OPENAI_API_KEY")


def start_api():
    """Start the FastAPI server"""
    print("🚀 Starting Echoes Research API...")
    print("   WebSocket endpoint: ws://localhost:8000/ws/stream")
    print("   API docs: http://localhost:8000/docs")
    print("   Health check: http://localhost:8000/health")
    print()

    try:
        # Use uvicorn to start the server
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            os.getenv("API_HOST", "0.0.0.0"),
            "--port",
            os.getenv("API_PORT", "8000"),
            "--workers",
            os.getenv("API_WORKERS", "1"),
            "--log-level",
            os.getenv("LOG_LEVEL", "info").lower(),
        ]

        if os.getenv("API_RELOAD", "true").lower() == "true":
            cmd.append("--reload")

        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False

    return True


def main():
    """Main startup function"""
    print("🎯 Echoes Research API Startup")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("api/main.py").exists():
        print("❌ Error: api/main.py not found")
        print("   Please run this script from the Echoes project root directory")
        sys.exit(1)

    # Create .env template if needed
    create_env_template()

    # Check environment
    if not check_environment():
        print("\n💡 Tip: Copy .env template and configure your API keys")
        sys.exit(1)

    # Start the API
    print()
    success = start_api()

    if success:
        print("\n✅ API startup completed successfully")
    else:
        print("\n❌ API startup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
