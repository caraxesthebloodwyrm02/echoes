"""
Echoes AI Cluster Management

This module provides cluster management functionality for the Echoes AI Multi-Agent System.
"""

import logging
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

from .config import get_settings

logger = logging.getLogger(__name__)


class ClusterType(Enum):
    KUBERNETES = "kubernetes"
    DOCKER_SWARM = "docker_swarm"
    LOCAL_DEV = "local_dev"
    MINIKUBE = "minikube"


@dataclass
class ClusterConfig:
    """Cluster configuration dataclass."""

    name: str
    type: ClusterType
    nodes: int = 3
    cpus: str = "2"
    memory: str = "4g"
    disk: str = "20g"
    network: str = "10.0.0.0/24"
    registry_port: int = 5000
    dashboard_port: int = 8080


class ClusterManager:
    """Manages cluster creation and operations."""

    def __init__(self, config: ClusterConfig):
        self.config = config
        self.settings = get_settings()
        self.project_root = Path(__file__).parent.parent
        self.cluster_dir = self.project_root / "clusters" / config.name

    def create_cluster(self) -> bool:
        """Create the cluster based on configuration."""
        print(f"🚀 Creating {self.config.type.value} cluster: {self.config.name}")

        if self.config.type == ClusterType.KUBERNETES:
            return self._create_kubernetes_cluster()
        elif self.config.type == ClusterType.DOCKER_SWARM:
            return self._create_docker_swarm()
        elif self.config.type == ClusterType.LOCAL_DEV:
            return self._create_local_dev()
        elif self.config.type == ClusterType.MINIKUBE:
            return self._create_minikube_cluster()
        else:
            print(f"❌ Unsupported cluster type: {self.config.type}")
            return False

    def _create_kubernetes_cluster(self) -> bool:
        """Create Kubernetes cluster using k3s or kubeadm."""
        print("📦 Setting up Kubernetes cluster...")

        # Create cluster directory
        self.cluster_dir.mkdir(parents=True, exist_ok=True)

        # Generate k3s configuration
        k3s_config = {
            "apiVersion": "k3s.cattle.io/v1",
            "kind": "Cluster",
            "metadata": {"name": self.config.name, "namespace": "fleet-default"},
            "spec": {
                "kubernetesVersion": "v1.28.3+k3s.1",
                "nodes": self.config.nodes,
                "rancherKubernetesEngineConfig": {
                    "ignoreDockerVersion": True,
                    "network": {"type": "calico"},
                },
            },
        }

        # Save configuration
        config_file = self.cluster_dir / "k3s-config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(k3s_config, f, default_flow_style=False)

        # Create docker-compose for Kubernetes
        docker_compose = {
            "version": "3.8",
            "services": {
                "k3s-server": {
                    "image": "rancher/k3s:latest",
                    "privileged": True,
                    "container_name": f"{self.config.name}-server",
                    "ports": ["6443:6443", f"{self.config.dashboard_port}:80"],
                    "volumes": [
                        "./k3s-server:/var/lib/rancher/k3s",
                        "/var/run/docker.sock:/var/run/docker.sock",
                    ],
                    "environment": [
                        "K3S_KUBECONFIG_OUTPUT=/k3s-config.yaml",
                        "K3S_KUBECONFIG_MODE=666",
                    ],
                    "command": "server --https-listen-port=6443 --no-deploy traefik",
                }
            },
        }

        # Save docker-compose
        compose_file = self.cluster_dir / "docker-compose.yaml"
        with open(compose_file, "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)

        print(f"✅ Kubernetes cluster configuration created at {self.cluster_dir}")
        return True

    def _create_docker_swarm(self) -> bool:
        """Create Docker Swarm cluster."""
        print("🐳 Setting up Docker Swarm cluster...")

        self.cluster_dir.mkdir(parents=True, exist_ok=True)

        # Create docker-compose for Swarm
        docker_compose = {
            "version": "3.8",
            "services": {
                "visualizer": {
                    "image": "dockersamples/visualizer:stable",
                    "ports": ["8080:8080"],
                    "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],
                    "deploy": {"placement": {"constraints": ["node.role == manager"]}},
                },
                "registry": {
                    "image": "registry:2",
                    "ports": [f"{self.config.registry_port}:5000"],
                    "volumes": ["./registry-data:/var/lib/registry"],
                    "deploy": {"replicas": 1},
                },
            },
        }

        compose_file = self.cluster_dir / "docker-compose.yaml"
        with open(compose_file, "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)

        print(f"✅ Docker Swarm configuration created at {self.cluster_dir}")
        return True

    def _create_local_dev(self) -> bool:
        """Create local development cluster."""
        print("💻 Setting up local development cluster...")

        self.cluster_dir.mkdir(parents=True, exist_ok=True)

        # Create docker-compose for local development
        docker_compose = {
            "version": "3.8",
            "services": {
                "redis": {"image": "redis:alpine", "ports": ["6379:6379"]},
                "postgres": {
                    "image": "postgres:15",
                    "environment": {
                        "POSTGRES_DB": "echoes",
                        "POSTGRES_USER": "echoes",
                        "POSTGRES_PASSWORD": "echoes123",
                    },
                    "ports": ["5432:5432"],
                    "volumes": ["./postgres-data:/var/lib/postgresql/data"],
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80"],
                    "volumes": ["./nginx.conf:/etc/nginx/nginx.conf"],
                },
            },
        }

        compose_file = self.cluster_dir / "docker-compose.yaml"
        with open(compose_file, "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)

        print(f"✅ Local development cluster created at {self.cluster_dir}")
        return True

    def _create_minikube_cluster(self) -> bool:
        """Create Minikube cluster."""
        print("⚡ Setting up Minikube cluster...")

        # Check if minikube is installed
        try:
            subprocess.run(["minikube", "version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Minikube not found. Please install Minikube first.")
            return False

        # Start minikube
        cmd = [
            "minikube",
            "start",
            "--name",
            self.config.name,
            "--nodes",
            str(self.config.nodes),
            "--cpus",
            self.config.cpus,
            "--memory",
            self.config.memory,
            "--disk-size",
            self.config.disk,
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Minikube cluster '{self.config.name}' started successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start Minikube cluster: {e}")
            return False

    def start_cluster(self) -> bool:
        """Start the cluster."""
        compose_file = self.cluster_dir / "docker-compose.yaml"
        if compose_file.exists():
            try:
                subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "up", "-d"],
                    check=True,
                    cwd=self.cluster_dir,
                )
                print(f"✅ Cluster '{self.config.name}' started successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start cluster: {e}")
                return False
        else:
            print("❌ No docker-compose.yaml found. Run create_cluster first.")
            return False

    def stop_cluster(self) -> bool:
        """Stop the cluster."""
        compose_file = self.cluster_dir / "docker-compose.yaml"
        if compose_file.exists():
            try:
                subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "down"],
                    check=True,
                    cwd=self.cluster_dir,
                )
                print(f"✅ Cluster '{self.config.name}' stopped successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to stop cluster: {e}")
                return False
        return False

    def get_cluster_status(self) -> dict:
        """Get cluster status."""
        status = {
            "name": self.config.name,
            "type": self.config.type.value,
            "status": "unknown",
        }

        if self.config.type == ClusterType.MINIKUBE:
            try:
                result = subprocess.run(
                    ["minikube", "status", "--name", self.config.name],
                    capture_output=True,
                    text=True,
                )
                status["status"] = "running" if result.returncode == 0 else "stopped"
                status["details"] = result.stdout.strip()
            except Exception as e:
                status["status"] = "error"
                status["error"] = str(e)
        else:
            # Check docker-compose status
            compose_file = self.cluster_dir / "docker-compose.yaml"
            if compose_file.exists():
                try:
                    result = subprocess.run(
                        ["docker-compose", "-f", str(compose_file), "ps"],
                        capture_output=True,
                        text=True,
                        cwd=self.cluster_dir,
                    )
                    status["status"] = (
                        "running" if result.returncode == 0 else "stopped"
                    )
                    status["details"] = result.stdout.strip()
                except Exception as e:
                    status["status"] = "error"
                    status["error"] = str(e)

        return status


def main():
    """Main cluster setup function."""
    print("🎯 Echoes AI Cluster Setup")
    print("=" * 50)

    # Default configuration
    config = ClusterConfig(
        name="echoes-cluster",
        type=ClusterType.LOCAL_DEV,
        nodes=3,
        cpus="2",
        memory="4g",
    )

    # Create cluster manager
    manager = ClusterManager(config)

    # Create cluster
    if manager.create_cluster():
        print(f"\n✅ Cluster '{config.name}' created successfully!")
        print(f"📍 Location: {manager.cluster_dir}")
        print(f"🔧 Type: {config.type.value}")

        # Start cluster
        if config.type != ClusterType.MINIKUBE:
            if manager.start_cluster():
                print("🚀 Cluster started successfully!")

        # Show status
        status = manager.get_cluster_status()
        print(f"\n📊 Cluster Status: {status['status']}")

        print("\n🎉 Cluster setup complete!")
        print("\nNext steps:")
        print(f"1. cd {manager.cluster_dir}")
        print("2. Check services with: docker-compose ps")
        print("3. View logs with: docker-compose logs -f")

    else:
        print("❌ Failed to create cluster")
        sys.exit(1)


if __name__ == "__main__":
    main()
