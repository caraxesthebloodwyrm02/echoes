#!/usr/bin/env python3
"""
Echoes API Server - Production Startup Script
=============================================

This script starts the Echoes API server in production mode.

Usage:
    python start_prod.py

Environment:
    - Optimized for production
    - No debug mode
    - Multiple workers for performance
"""

import os
import sys
import multiprocessing
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Start the API server in production mode."""
    # Set production environment variables
    os.environ.setdefault("ECHOES_API_DEBUG", "false")
    os.environ.setdefault("ECHOES_API_HOST", "0.0.0.0")
    os.environ.setdefault("ECHOES_API_PORT", "8000")

    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")
        except ImportError:
            print("python-dotenv not installed, using system environment")

    print("Starting Echoes API Server (Production Mode)")
    print(f"Host: {os.getenv('ECHOES_API_HOST', '0.0.0.0')}")
    print(f"Port: {os.getenv('ECHOES_API_PORT', '8000')}")
    print("Auto-reload: Disabled")
    print("Debug mode: Disabled")
    print()

    # Calculate optimal number of workers
    cpu_count = multiprocessing.cpu_count()
    workers = min(cpu_count, 4)  # Max 4 workers to avoid overwhelming small servers
    print(f"Using {workers} worker(s) ({cpu_count} CPU cores available)")

    # Import and run the server
    try:
        from echoes.api.server import app
        import uvicorn

        uvicorn.run(
            "echoes.api.server:app",
            host=os.getenv("ECHOES_API_HOST", "0.0.0.0"),
            port=int(os.getenv("ECHOES_API_PORT", "8000")),
            workers=workers,
            reload=False,
            log_level="info",
            access_log=True,
            server_header=False,  # Hide server info for security
            date_header=False,  # Hide date for security
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
