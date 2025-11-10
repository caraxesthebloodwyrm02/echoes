#!/usr/bin/env python3
"""
Cluster status monitoring script for Echoes
"""

import json
import subprocess
from datetime import datetime


def get_docker_status():
    """Get Docker container status"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        containers = [
            json.loads(line) for line in result.stdout.strip().split("\n") if line
        ]
        return containers
    except Exception as e:
        print(f"❌ Error getting Docker status: {e}")
        return []


def check_service_health():
    """Check health of individual services"""
    services = {
        "Main App": "http://localhost:8000/health",
        "Nginx": "http://localhost/health",
        "Grafana": "http://localhost:3000/api/health",
        "Prometheus": "http://localhost:9090/-/healthy",
        "Redis": "localhost:6379",
        "PostgreSQL": "localhost:5432",
    }

    health_status = {}

    for service, endpoint in services.items():
        try:
            if endpoint.startswith("http"):
                # Use curl for HTTP endpoints
                result = subprocess.run(
                    ["curl", "-f", "-s", endpoint],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                health_status[service] = (
                    "✅ Healthy" if result.returncode == 0 else "❌ Unhealthy"
                )
            else:
                # For TCP endpoints, just check if they're listening
                host, port = endpoint.split(":")
                result = subprocess.run(
                    ["nc", "-z", host, port], capture_output=True, timeout=5
                )
                health_status[service] = (
                    "✅ Connected" if result.returncode == 0 else "❌ Disconnected"
                )
        except Exception as e:
            health_status[service] = f"❌ Error: {str(e)[:50]}"

    return health_status


def get_resource_usage():
    """Get resource usage statistics"""
    try:
        result = subprocess.run(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except Exception as e:
        return f"Error getting stats: {e}"


def main():
    """Display cluster status"""
    print("📊 Echoes Cluster Status")
    print("=" * 50)
    print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Docker container status
    print("🐳 Docker Containers:")
    containers = get_docker_status()
    if containers:
        for container in containers:
            name = container.get("Names", "Unknown")
            status = container.get("State", "Unknown")
            ports = container.get("Ports", "None")
            print(f"  {name}: {status}")
            if ports != "None":
                print(f"    Ports: {ports}")
    else:
        print("  No containers running")
    print()

    # Service health
    print("🏥 Service Health:")
    health = check_service_health()
    for service, status in health.items():
        print(f"  {service}: {status}")
    print()

    # Resource usage
    print("📈 Resource Usage:")
    usage = get_resource_usage()
    print(usage)
    print()

    # Quick commands
    print("🔧 Quick Commands:")
    print(
        "  View logs: docker-compose -f clusters/echoes-cluster/docker-compose.yaml logs -f"
    )
    print(
        "  Stop cluster: docker-compose -f clusters/echoes-cluster/docker-compose.yaml down"
    )
    print(
        "  Restart service: docker-compose -f clusters/echoes-cluster/docker-compose.yaml restart [service]"
    )
    print("  Access container: docker exec -it [container_name] /bin/bash")


if __name__ == "__main__":
    main()
