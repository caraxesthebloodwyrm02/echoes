#!/usr/bin/env python3
"""
Simple cluster startup script for Echoes
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    """Start the Echoes cluster"""
    print("🚀 Starting Echoes Cluster")
    print("=" * 40)

    cluster_dir = Path("clusters/echoes-cluster")

    if not cluster_dir.exists():
        print("❌ Cluster directory not found. Run cluster_setup.py first.")
        sys.exit(1)

    # Check if Docker is available
    if not run_command("docker --version", "Checking Docker installation"):
        print("❌ Docker is not installed or not running.")
        print(
            "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
        )
        sys.exit(1)

    # Start the cluster
    compose_file = cluster_dir / "docker-compose.yaml"
    if compose_file.exists():
        if run_command(
            f"docker-compose -f {compose_file} up -d",
            "Starting cluster services",
            cwd=cluster_dir,
        ):
            print("\n✅ Cluster started successfully!")
            print("\n📊 Services available at:")
            print("  - Main App: http://localhost:8000")
            print("  - Nginx Proxy: http://localhost")
            print("  - Grafana: http://localhost:3000 (admin/admin123)")
            print("  - Prometheus: http://localhost:9090")
            print("  - Jaeger: http://localhost:16686")
            print("\n🔍 Check status with: docker-compose ps")
            print("📋 View logs with: docker-compose logs -f")
        else:
            print("❌ Failed to start cluster")
            sys.exit(1)
    else:
        print("❌ docker-compose.yaml not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
