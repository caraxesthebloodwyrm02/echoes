"""
Ecosystem-inspired resilience patterns for the Echoes platform.

This module implements various resilience patterns inspired by natural ecosystems:
- HerdImmunityRateLimiter: Adaptive rate limiting based on system health
- SymbioticService: Mutualistic service communication
- HibernationManager: Resource conservation during low activity
- SchoolingLoadBalancer: Coordinated load distribution
- DecoySystem: Security through deception

These patterns help create more resilient, adaptive, and sustainable systems.
"""

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class HerdImmunityRateLimiter:
    """
    Implements adaptive rate limiting based on the health of system instances.
    Inspired by herd immunity in nature where the health of the majority
    protects the entire population.
    """

    def __init__(self, base_rate: int = 100, herd_immunity_threshold: float = 0.7):
        """
        Initialize the herd immunity rate limiter.

        Args:
            base_rate: Base requests per second when system is fully healthy
            herd_immunity_threshold: Minimum ratio of healthy instances for full capacity
        """
        self.base_rate = base_rate
        self.herd_immunity_threshold = herd_immunity_threshold
        self.healthy_instances: list[str] = []
        self.total_instances: int = 0

    def update_health_status(self, instance_id: str, is_healthy: bool) -> None:
        """
        Update the health status of a system instance.

        Args:
            instance_id: Unique identifier for the instance
            is_healthy: Whether the instance is currently healthy
        """
        if is_healthy:
            if instance_id not in self.healthy_instances:
                self.healthy_instances.append(instance_id)
        else:
            self.healthy_instances = [
                i for i in self.healthy_instances if i != instance_id
            ]

    def get_effective_rate_limit(self) -> int:
        """
        Calculate the effective rate limit based on current system health.

        Returns:
            Adjusted rate limit in requests per second
        """
        if self.total_instances == 0:
            return self.base_rate

        healthy_ratio = len(self.healthy_instances) / self.total_instances

        if healthy_ratio >= self.herd_immunity_threshold:
            return self.base_rate  # Full capacity
        else:
            # Scale down requests to protect the system
            adjusted_rate = int(
                self.base_rate * (healthy_ratio / self.herd_immunity_threshold)
            )
            logger.info(
                f"Rate limited: {adjusted_rate} req/s (healthy ratio: {healthy_ratio:.2f})"
            )
            return adjusted_rate


class SymbioticService:
    """
    Implements mutualistic relationships between services.
    Inspired by symbiosis in nature where species work together for mutual benefit.
    """

    def __init__(self):
        """Initialize the symbiotic service."""
        self.partners: dict[str, dict[str, Any]] = {}
        self.resources: dict[str, dict[str, Any]] = {}

    def register_partner(
        self, service_name: str, benefit_callback: Callable, cost_callback: Callable
    ) -> None:
        """
        Register a partner service with give/take callbacks.

        Args:
            service_name: Name of the partner service
            benefit_callback: Function called when partner provides benefit
            cost_callback: Function called to calculate cost of resource
        """
        self.partners[service_name] = {
            "benefit": benefit_callback,
            "cost": cost_callback,
            "last_interaction": None,
        }
        logger.info(f"Registered symbiotic partner: {service_name}")

    def add_resource(self, resource_name: str, data: Any, available: int = 1) -> None:
        """
        Add a resource that can be shared with partners.

        Args:
            resource_name: Name of the resource
            data: The actual resource data
            available: Number of times this resource can be used
        """
        self.resources[resource_name] = {
            "data": data,
            "available": available,
            "total_provided": 0,
        }

    def request_resource(
        self, resource_name: str, from_service: str
    ) -> dict[str, Any] | None:
        """
        Request a resource from a partner service.

        Args:
            resource_name: Name of the requested resource
            from_service: Name of the requesting service

        Returns:
            Resource data and cost information, or None if unavailable
        """
        if from_service not in self.partners:
            raise ValueError(f"No symbiotic relationship with {from_service}")

        # What does it cost the requester to get this resource?
        cost = self.partners[from_service]["cost"](resource_name)

        # Can we provide the resource?
        if (
            resource_name in self.resources
            and self.resources[resource_name]["available"] > 0
        ):
            self.resources[resource_name]["available"] -= 1
            self.resources[resource_name]["total_provided"] += 1
            self.partners[from_service]["last_interaction"] = time.time()

            logger.debug(f"Resource {resource_name} provided to {from_service}")

            return {
                "resource": resource_name,
                "data": self.resources[resource_name]["data"],
                "cost": cost,
                "timestamp": time.time(),
            }

        return None


class HibernationManager:
    """
    Implements resource conservation during periods of low activity.
    Inspired by animal hibernation to conserve energy during scarce periods.
    """

    def __init__(self, min_utilization: float = 0.2, max_inactivity: int = 3600):
        """
        Initialize the hibernation manager.

        Args:
            min_utilization: Minimum utilization threshold before considering hibernation
            max_inactivity: Maximum seconds of inactivity before hibernating
        """
        self.min_utilization = min_utilization
        self.max_inactivity = max_inactivity
        self.last_activity = time.time()
        self.hibernating = False
        self.saved_state = {}

    def log_activity(self) -> None:
        """
        Log system activity to prevent hibernation.
        """
        self.last_activity = time.time()
        if self.hibernating:
            self._wake_up()

    def check_hibernation(self, current_utilization: float) -> None:
        """
        Check if system should enter hibernation based on current metrics.

        Args:
            current_utilization: Current system utilization (0.0 to 1.0)
        """
        inactive_duration = time.time() - self.last_activity

        if (
            current_utilization < self.min_utilization
            and inactive_duration > self.max_inactivity
            and not self.hibernating
        ):
            self._initiate_hibernation()

    def _initiate_hibernation(self) -> None:
        """Enter hibernation mode to conserve resources."""
        self.hibernating = True
        self.saved_state = {
            "timestamp": time.time(),
            "last_activity": self.last_activity,
        }
        logger.info("Entering hibernation mode to conserve resources")

        # Here you would implement actual resource conservation:
        # - Reduce thread pools
        # - Pause non-essential services
        # - Lower cache sizes
        # - Save state to disk

    def _wake_up(self) -> None:
        """Wake up from hibernation and restore normal operation."""
        self.hibernating = False
        logger.info("Waking up from hibernation")

        # Here you would implement restoration:
        # - Restore thread pools
        # - Resume services
        # - Reload caches
        # - Restore state from disk


class SchoolingLoadBalancer:
    """
    Implements coordinated load distribution across multiple nodes.
    Inspired by schooling behavior in fish where individuals coordinate movements.
    """

    def __init__(self, nodes: list[Any], coordination_threshold: float = 0.7):
        """
        Initialize the schooling load balancer.

        Args:
            nodes: List of available service nodes
            coordination_threshold: Consensus threshold for direction changes
        """
        self.nodes = nodes
        self.coordination_threshold = coordination_threshold
        self.last_direction = None
        self.load_history = defaultdict(list)

    def get_target_node(self, request: Any) -> Any:
        """
        Select a target node for the given request.

        Args:
            request: The request to be processed

        Returns:
            Selected node for processing
        """
        # Simple round-robin when no coordination needed
        if len(self.nodes) == 1:
            return self.nodes[0]

        # Check if we need to coordinate a movement
        if self._needs_coordination():
            self._coordinate_movement()

        # Select node based on current direction
        return self._select_node_by_direction(request)

    def _needs_coordination(self) -> bool:
        """
        Check if load is unevenly distributed and needs coordination.

        Returns:
            True if coordination is needed
        """
        if len(self.nodes) < 2:
            return False

        loads = [node.get_load() for node in self.nodes]
        return max(loads) - min(loads) > 0.3  # 30% difference threshold

    def _coordinate_movement(self) -> None:
        """
        Coordinate movement direction based on node consensus.
        """
        # Nodes "vote" on direction changes
        votes = defaultdict(int)
        for node in self.nodes:
            direction = node.get_preferred_direction()
            votes[direction] += 1

        # Find the direction with consensus
        for direction, count in votes.items():
            if count / len(self.nodes) >= self.coordination_threshold:
                self.last_direction = direction
                logger.debug(f"Coordinated movement direction: {direction}")
                break

    def _select_node_by_direction(self, request: Any) -> Any:
        """
        Select node based on the current coordinated direction.

        Args:
            request: The request to be processed

        Returns:
            Selected node
        """
        # Implement direction-based selection
        # This is a simplified example - real implementation would be more sophisticated
        if self.last_direction == "north":
            # Select node with lowest position (simplified)
            return min(self.nodes, key=lambda n: getattr(n, "position", [0, 0])[1])
        elif self.last_direction == "south":
            # Select node with highest position
            return max(self.nodes, key=lambda n: getattr(n, "position", [0, 0])[1])
        elif self.last_direction == "east":
            # Select node with highest x position
            return max(self.nodes, key=lambda n: getattr(n, "position", [0, 0])[0])
        elif self.last_direction == "west":
            # Select node with lowest x position
            return min(self.nodes, key=lambda n: getattr(n, "position", [0, 0])[0])

        # Fallback to least loaded node
        return min(self.nodes, key=lambda n: n.get_load())


class DecoySystem:
    """
    Implements security through deception using decoy targets.
    Inspired by decoy behaviors in nature where animals distract predators.
    """

    def __init__(self):
        """Initialize the decoy system."""
        self.decoys: dict[str, dict[str, Any]] = {}
        self.attack_patterns: dict[str, int] = {}
        self.blocked_ips = set()

    def create_decoy(self, decoy_type: str, location: str) -> str:
        """
        Create a fake high-value target to attract attackers.

        Args:
            decoy_type: Type of decoy (e.g., 'high_value', 'database', 'api')
            location: Network location of the decoy

        Returns:
            Unique identifier for the created decoy
        """
        decoy_id = f"decoy_{len(self.decoys) + 1}"
        self.decoys[decoy_id] = {
            "type": decoy_type,
            "location": location,
            "created": time.time(),
            "interactions": 0,
            "last_interaction": None,
            "active": True,
        }
        logger.info(f"Created decoy {decoy_id} of type {decoy_type} at {location}")
        return decoy_id

    def monitor_interaction(
        self, decoy_id: str, interaction_type: str, source_ip: str
    ) -> bool:
        """
        Monitor and log interactions with decoys.

        Args:
            decoy_id: ID of the decoy being interacted with
            interaction_type: Type of interaction (e.g., 'scan', 'probe', 'attack')
            source_ip: IP address of the source

        Returns:
            True if interaction was logged successfully
        """
        if decoy_id not in self.decoys or not self.decoys[decoy_id]["active"]:
            return False

        self.decoys[decoy_id]["interactions"] += 1
        self.decoys[decoy_id]["last_interaction"] = time.time()

        # Log the attack pattern
        attack_signature = f"{interaction_type}_{source_ip}"
        self.attack_patterns[attack_signature] = (
            self.attack_patterns.get(attack_signature, 0) + 1
        )

        logger.warning(
            f"Decoy interaction: {decoy_id} - {interaction_type} from {source_ip}"
        )

        # If this is a known attack pattern, trigger response
        if self.attack_patterns[attack_signature] > 3:  # Threshold for repeated attacks
            self._initiate_countermeasures(source_ip)

        return True

    def _initiate_countermeasures(self, source_ip: str) -> None:
        """
        Initiate security countermeasures against the source.

        Args:
            source_ip: IP address to apply countermeasures to
        """
        logger.warning(f"Initiating countermeasures against {source_ip}")
        self.blocked_ips.add(source_ip)

        # Implementation depends on your security infrastructure:
        # - Block IP at firewall
        # - Increase monitoring on this IP
        # - Alert security team
        # - Create additional decoys for this attacker

    def get_security_report(self) -> dict[str, Any]:
        """
        Generate a security report from decoy interactions.

        Returns:
            Summary of security metrics and findings
        """
        total_interactions = sum(
            decoy["interactions"] for decoy in self.decoys.values()
        )
        active_decoys = sum(1 for decoy in self.decoys.values() if decoy["active"])

        return {
            "total_decoys": len(self.decoys),
            "active_decoys": active_decoys,
            "total_interactions": total_interactions,
            "blocked_ips": len(self.blocked_ips),
            "attack_patterns": len(self.attack_patterns),
            "top_attackers": sorted(
                self.attack_patterns.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


# Utility functions for ecosystem integration
def create_resilient_system(
    base_rate: int = 100, num_instances: int = 5
) -> dict[str, Any]:
    """
    Create a complete resilient system with all ecosystem components.

    Args:
        base_rate: Base rate limit for the system
        num_instances: Number of service instances

    Returns:
        Dictionary containing all initialized components
    """
    return {
        "rate_limiter": HerdImmunityRateLimiter(base_rate=base_rate),
        "hibernation_manager": HibernationManager(),
        "decoy_system": DecoySystem(),
        "symbiotic_service": SymbioticService(),
    }


def monitor_ecosystem_health(components: dict[str, Any]) -> dict[str, Any]:
    """
    Monitor the health of all ecosystem components.

    Args:
        components: Dictionary of ecosystem components

    Returns:
        Health status of all components
    """
    health_report = {"timestamp": time.time(), "components": {}}

    # Check rate limiter health
    if "rate_limiter" in components:
        rl = components["rate_limiter"]
        health_report["components"]["rate_limiter"] = {
            "healthy_instances": len(rl.healthy_instances),
            "total_instances": rl.total_instances,
            "effective_rate": rl.get_effective_rate_limit(),
        }

    # Check hibernation status
    if "hibernation_manager" in components:
        hm = components["hibernation_manager"]
        health_report["components"]["hibernation_manager"] = {
            "hibernating": hm.hibernating,
            "inactive_duration": time.time() - hm.last_activity,
        }

    # Check decoy system
    if "decoy_system" in components:
        ds = components["decoy_system"]
        health_report["components"]["decoy_system"] = ds.get_security_report()

    return health_report
