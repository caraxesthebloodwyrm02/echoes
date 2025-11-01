#!/usr/bin/env python3
"""
Echoes API Server - Development Startup Script
==============================================

This script starts the Echoes API server in development mode.

Usage:
    python start_dev.py

Environment:
    - Debug mode enabled
    - Auto-reload enabled
    - Default development API key loaded
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Start the API server in development mode."""
    # Set development environment variables
    os.environ.setdefault("ECHOES_API_DEBUG", "true")
    os.environ.setdefault("ECHOES_API_HOST", "127.0.0.1")
    os.environ.setdefault("ECHOES_API_PORT", "8000")

    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")
        except ImportError:
            print("python-dotenv not installed, skipping .env file loading")

    print("Starting Echoes API Server (Development Mode)")
    print(f"Host: {os.getenv('ECHOES_API_HOST', '127.0.0.1')}")
    print(f"Port: {os.getenv('ECHOES_API_PORT', '8000')}")
    print("Auto-reload: Enabled")
    print("Debug mode: Enabled")
    print()

    # Import and run the server
    try:
        print(f"Project root: {project_root}")
        print(f"Python path: {sys.path[:3]}")

        from echoes.api.server import app
        import uvicorn

        uvicorn.run(
            "echoes.api.server:app",
            host=os.getenv("ECHOES_API_HOST", "127.0.0.1"),
            port=int(os.getenv("ECHOES_API_PORT", "8000")),
            reload=True,
            reload_dirs=[str(project_root)],
            log_level="info",
            access_log=True,
        )

    except ImportError as e:
        print(f"Failed to import server: {e}")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
