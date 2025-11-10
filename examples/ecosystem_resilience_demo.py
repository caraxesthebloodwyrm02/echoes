"""
Ecosystem Resilience Demo
==========================

This demo showcases how nature-inspired patterns create more resilient,
adaptive, and sustainable systems. Each pattern draws inspiration from
natural ecosystems to solve common software engineering challenges.

Patterns Demonstrated:
1. HerdImmunityRateLimiter - Adaptive rate limiting based on system health
2. SymbioticService - Mutualistic service communication
3. HibernationManager - Resource conservation during low activity
4. SchoolingLoadBalancer - Coordinated load distribution
5. DecoySystem - Security through deception

Run with: python examples/ecosystem_resilience_demo.py
"""

import os
import random
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.ecosystem_resilience import (
    DecoySystem,
    HerdImmunityRateLimiter,
    HibernationManager,
    SchoolingLoadBalancer,
    SymbioticService,
    create_resilient_system,
    monitor_ecosystem_health,
)


class MockServiceNode:
    """Mock service node for load balancer demonstration."""

    def __init__(self, node_id, position=None):
        self.node_id = node_id
        self.position = position or [random.randint(0, 100), random.randint(0, 100)]
        self.current_load = random.uniform(0.1, 0.9)

    def get_load(self):
        """Get current load on this node."""
        return self.current_load

    def get_preferred_direction(self):
        """Get preferred direction for load balancing."""
        directions = ["north", "south", "east", "west"]
        return random.choice(directions)

    def process_request(self, request):
        """Simulate processing a request."""
        # Simulate processing time
        time.sleep(0.01)
        # Randomly adjust load
        self.current_load = max(
            0.1, min(0.9, self.current_load + random.uniform(-0.1, 0.1))
        )
        return f"Processed by {self.node_id}"


def demo_herd_immunity_rate_limiter():
    """Demonstrate adaptive rate limiting based on system health."""
    print("\n" + "=" * 60)
    print("🦓 HERD IMMUNITY RATE LIMITER DEMO")
    print("=" * 60)

    # Create rate limiter with 5 instances
    limiter = HerdImmunityRateLimiter(base_rate=100, herd_immunity_threshold=0.7)
    limiter.total_instances = 5

    print(
        f"\nInitial setup: {limiter.total_instances} instances, threshold={limiter.herd_immunity_threshold}"
    )
    print(f"Base rate: {limiter.base_rate} requests/second")

    # Scenario 1: All instances healthy
    print("\n--- Scenario 1: All instances healthy ---")
    for i in range(5):
        limiter.update_health_status(f"instance_{i}", True)

    effective_rate = limiter.get_effective_rate_limit()
    print(f"Healthy instances: {len(limiter.healthy_instances)}/5")
    print(f"Effective rate limit: {effective_rate} req/s")
    print("✅ Full capacity maintained")

    # Scenario 2: Some instances unhealthy
    print("\n--- Scenario 2: 2 out of 5 instances unhealthy ---")
    limiter.update_health_status("instance_3", False)
    limiter.update_health_status("instance_4", False)

    effective_rate = limiter.get_effective_rate_limit()
    healthy_ratio = len(limiter.healthy_instances) / limiter.total_instances
    print(
        f"Healthy instances: {len(limiter.healthy_instances)}/5 ({healthy_ratio:.1%})"
    )
    print(f"Effective rate limit: {effective_rate} req/s")
    print("⚠️ Rate reduced to protect remaining instances")

    # Scenario 3: Critical failure
    print("\n--- Scenario 3: Only 1 instance healthy ---")
    limiter.update_health_status("instance_0", False)
    limiter.update_health_status("instance_1", False)

    effective_rate = limiter.get_effective_rate_limit()
    healthy_ratio = len(limiter.healthy_instances) / limiter.total_instances
    print(
        f"Healthy instances: {len(limiter.healthy_instances)}/5 ({healthy_ratio:.1%})"
    )
    print(f"Effective rate limit: {effective_rate} req/s")
    print("🚨 Critical rate limiting activated")

    print("\n💡 This pattern prevents cascading failures by adapting to system health!")


def demo_symbiotic_service():
    """Demonstrate mutualistic service relationships."""
    print("\n" + "=" * 60)
    print("🤝 SYMBIOTIC SERVICE DEMO")
    print("=" * 60)

    # Create symbiotic service
    service = SymbioticService()

    # Add resources
    service.add_resource("compute_power", {"cpu_cores": 8, "memory_gb": 32}, 10)
    service.add_resource("storage_space", {"type": "ssd", "size_gb": 1000}, 5)
    service.add_resource("api_calls", {"endpoint": "/process", "rate_limit": 1000}, 100)

    print("\nAvailable resources:")
    for name, resource in service.resources.items():
        print(f"  - {name}: {resource['available']} units available")

    # Register partner services
    def compute_benefit(resource_name):
        return f"Processing benefit from {resource_name}"

    def compute_cost(resource_name):
        costs = {"compute_power": 5, "storage_space": 2, "api_calls": 1}
        return costs.get(resource_name, 0)

    def storage_benefit(resource_name):
        return f"Storage benefit from {resource_name}"

    def storage_cost(resource_name):
        costs = {"compute_power": 3, "storage_space": 1, "api_calls": 2}
        return costs.get(resource_name, 0)

    service.register_partner("compute_service", compute_benefit, compute_cost)
    service.register_partner("storage_service", storage_benefit, storage_cost)

    print("\n--- Resource Exchange ---")

    # Compute service requests resources
    print("\nCompute Service requests:")
    for resource in ["compute_power", "storage_space", "api_calls"]:
        result = service.request_resource(resource, "compute_service")
        if result:
            benefit = compute_benefit(resource)
            print(f"  ✅ {resource}: cost={result['cost']}, benefit='{benefit}'")
        else:
            print(f"  ❌ {resource}: unavailable")

    # Storage service requests resources
    print("\nStorage Service requests:")
    for resource in ["compute_power", "storage_space", "api_calls"]:
        result = service.request_resource(resource, "storage_service")
        if result:
            benefit = storage_benefit(resource)
            print(f"  ✅ {resource}: cost={result['cost']}, benefit='{benefit}'")
        else:
            print(f"  ❌ {resource}: unavailable")

    print("\nRemaining resources:")
    for name, resource in service.resources.items():
        print(f"  - {name}: {resource['available']} units available")

    print("\n💡 This pattern enables efficient resource sharing between services!")


def demo_hibernation_manager():
    """Demonstrate resource conservation through hibernation."""
    print("\n" + "=" * 60)
    print("🐻 HIBERNATION MANAGER DEMO")
    print("=" * 60)

    # Create hibernation manager
    manager = HibernationManager(
        min_utilization=0.2, max_inactivity=5
    )  # 5 seconds for demo

    print("\nConfiguration:")
    print(f"  - Min utilization threshold: {manager.min_utilization:.1%}")
    print(f"  - Max inactivity before hibernation: {manager.max_inactivity} seconds")
    print(f"  - Current state: {'Hibernating' if manager.hibernating else 'Active'}")

    # Simulate system activity
    print("\n--- Simulating System Activity ---")

    # High utilization - no hibernation
    print("\n1. High utilization (50%) with recent activity:")
    manager.check_hibernation(0.5)  # 50% utilization
    print(f"   State: {'Hibernating' if manager.hibernating else 'Active'} ✅")

    # Low utilization but recent activity - no hibernation
    print("\n2. Low utilization (10%) but recent activity:")
    manager.log_activity()  # Log activity
    manager.check_hibernation(0.1)  # 10% utilization
    print(f"   State: {'Hibernating' if manager.hibernating else 'Active'} ✅")

    # Low utilization and no activity - trigger hibernation
    print("\n3. Low utilization (10%) with no activity for 6 seconds:")
    manager.last_activity = time.time() - 6  # Simulate 6 seconds of inactivity
    manager.check_hibernation(0.1)  # 10% utilization
    print(f"   State: {'Hibernating' if manager.hibernating else 'Active'} 🐻")

    # Wake up on activity
    print("\n4. Activity detected during hibernation:")
    manager.log_activity()  # Log new activity
    print(f"   State: {'Hibernating' if manager.hibernating else 'Active'} ⚡")

    print("\n💡 This pattern conserves resources during periods of low activity!")


def demo_schooling_load_balancer():
    """Demonstrate coordinated load distribution."""
    print("\n" + "=" * 60)
    print("🐟 SCHOOLING LOAD BALANCER DEMO")
    print("=" * 60)

    # Create mock nodes
    nodes = [
        MockServiceNode("Node_1", [10, 20]),
        MockServiceNode("Node_2", [30, 40]),
        MockServiceNode("Node_3", [50, 60]),
        MockServiceNode("Node_4", [70, 80]),
        MockServiceNode("Node_5", [90, 100]),
    ]

    # Create load balancer
    balancer = SchoolingLoadBalancer(nodes, coordination_threshold=0.6)

    print("\nLoad Balancer Configuration:")
    print(f"  - Number of nodes: {len(nodes)}")
    print(f"  - Coordination threshold: {balancer.coordination_threshold:.1%}")

    print("\n--- Initial Load Distribution ---")
    for node in nodes:
        print(f"  {node.node_id}: load={node.get_load():.2f}, position={node.position}")

    # Simulate load balancing
    print("\n--- Processing Requests ---")
    request_count = 20
    node_usage = {node.node_id: 0 for node in nodes}

    for i in range(request_count):
        request = f"request_{i}"
        selected_node = balancer.get_target_node(request)
        selected_node.process_request(request)
        node_usage[selected_node.node_id] += 1

    print(f"\nProcessed {request_count} requests")
    print("\nFinal Load Distribution:")
    for node in nodes:
        print(
            f"  {node.node_id}: load={node.get_load():.2f}, requests={node_usage[node.node_id]}"
        )

    # Check if coordination was needed
    print(f"\nCoordination needed: {balancer._needs_coordination()}")
    print(f"Last direction: {balancer.last_direction}")

    print("\n💡 This pattern coordinates load distribution like a fish school!")


def demo_decoy_system():
    """Demonstrate security through deception."""
    print("\n" + "=" * 60)
    print("🎭 DECOY SECURITY SYSTEM DEMO")
    print("=" * 60)

    # Create decoy system
    decoy_system = DecoySystem()

    # Create decoys
    decoys = [
        decoy_system.create_decoy("admin_panel", "dmz"),
        decoy_system.create_decoy("database", "internal_network"),
        decoy_system.create_decoy("api_endpoint", "public"),
        decoy_system.create_decoy("file_server", "dmz"),
    ]

    print(f"\nCreated {len(decoys)} decoys:")
    for decoy_id in decoys:
        decoy = decoy_system.decoys[decoy_id]
        print(f"  - {decoy_id}: {decoy['type']} at {decoy['location']}")

    # Simulate attacks
    print("\n--- Simulating Attacks ---")
    attacks = [
        ("192.168.1.100", "scan"),
        ("192.168.1.100", "probe"),
        ("10.0.0.50", "scan"),
        ("192.168.1.100", "attack"),  # Repeated attacker
        ("10.0.0.50", "probe"),
        ("172.16.0.10", "scan"),
        ("192.168.1.100", "brute_force"),  # Trigger countermeasures
    ]

    for ip, attack_type in attacks:
        target_decoy = random.choice(decoys)
        result = decoy_system.monitor_interaction(target_decoy, attack_type, ip)
        if result:
            print(f"  🎯 {ip} -> {target_decoy} ({attack_type})")
        else:
            print(f"  ❌ {ip} -> {target_decoy} ({attack_type}) - blocked")

    # Generate security report
    print("\n--- Security Report ---")
    report = decoy_system.get_security_report()

    print(f"Total interactions: {report['total_interactions']}")
    print(f"Blocked IPs: {report['blocked_ips']}")
    print(f"Attack patterns detected: {report['attack_patterns']}")

    if report["top_attackers"]:
        print("\nTop attackers:")
        for pattern, count in report["top_attackers"][:3]:
            print(f"  - {pattern}: {count} attempts")

    print("\n💡 This pattern uses deception to detect and block attackers!")


def demo_integrated_ecosystem():
    """Demonstrate all patterns working together."""
    print("\n" + "=" * 60)
    print("🌍 INTEGRATED ECOSYSTEM DEMO")
    print("=" * 60)

    # Create complete resilient system
    ecosystem = create_resilient_system(base_rate=100, num_instances=5)

    print("\nCreated integrated ecosystem with:")
    for component_name in ecosystem.keys():
        print(f"  - {component_name}")

    # Simulate system operation
    print("\n--- Simulating System Operation ---")

    # Configure rate limiter
    rate_limiter = ecosystem["rate_limiter"]
    rate_limiter.total_instances = 5
    for i in range(5):
        rate_limiter.update_health_status(f"instance_{i}", True)

    # Add resources to symbiotic service
    symbiotic = ecosystem["symbiotic_service"]
    symbiotic.add_resource("compute", {"cores": 4}, 10)
    symbiotic.add_resource("storage", {"gb": 100}, 5)

    def benefit_func(r):
        return f"Benefit from {r}"

    def cost_func(r):
        return 1 if r == "compute" else 2

    symbiotic.register_partner("worker", benefit_func, cost_func)

    # Simulate gradual system degradation
    print("\n1. System running normally:")
    health = monitor_ecosystem_health(ecosystem)
    print(
        f"   Rate limit: {health['components']['rate_limiter']['effective_rate']} req/s"
    )
    print(
        f"   Hibernating: {health['components']['hibernation_manager']['hibernating']}"
    )

    print("\n2. Some instances failing:")
    rate_limiter.update_health_status("instance_2", False)
    rate_limiter.update_health_status("instance_3", False)
    health = monitor_ecosystem_health(ecosystem)
    print(
        f"   Rate limit: {health['components']['rate_limiter']['effective_rate']} req/s"
    )
    print(
        f"   Healthy instances: {health['components']['rate_limiter']['healthy_instances']}/5"
    )

    print("\n3. Resource sharing active:")
    result = symbiotic.request_resource("compute", "worker")
    if result:
        print(f"   Resource allocated: {result['resource']} (cost: {result['cost']})")

    print("\n4. Security monitoring active:")
    decoy = ecosystem["decoy_system"]
    decoy_id = decoy.create_decoy("api", "public")
    decoy.monitor_interaction(decoy_id, "scan", "attacker_ip")
    report = decoy.get_security_report()
    print(f"   Security events: {report['total_interactions']}")

    print("\n✅ Integrated ecosystem successfully handles multiple challenges!")

    # Final health summary
    print("\n--- Final System Health ---")
    final_health = monitor_ecosystem_health(ecosystem)
    for component, status in final_health["components"].items():
        print(f"  {component}: {status}")

    print("\n💡 All patterns work together to create a resilient, adaptive system!")


def main():
    """Run all ecosystem resilience demonstrations."""
    print("\n🌿 ECOSYSTEM RESILIENCE PATTERNS DEMO")
    print("=" * 60)
    print("\nThis demo showcases nature-inspired patterns for building")
    print("more resilient, adaptive, and sustainable software systems.")
    print("\nPatterns inspired by:")
    print("  🦓 Herd immunity - Adaptive rate limiting")
    print("  🤝 Symbiosis - Mutual service relationships")
    print("  🐻 Hibernation - Resource conservation")
    print("  🐟 Schooling - Coordinated load balancing")
    print("  🎭 Decoys - Security through deception")

    # Run individual demos
    demo_herd_immunity_rate_limiter()
    demo_symbiotic_service()
    demo_hibernation_manager()
    demo_schooling_load_balancer()
    demo_decoy_system()

    # Run integrated demo
    demo_integrated_ecosystem()

    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  1. Natural ecosystems have evolved elegant solutions")
    print("  2. These patterns can be applied to software systems")
    print("  3. Resilience comes from adaptation, not just strength")
    print("  4. Multiple patterns work better together")
    print("  5. Sustainability is as important as performance")

    print("\nNext Steps:")
    print("  - Integrate these patterns into your existing systems")
    print("  - Monitor and measure their effectiveness")
    print("  - Adapt the patterns to your specific needs")
    print("  - Share your findings with the community")

    print("\n🌍 Building better systems, inspired by nature!")


if __name__ == "__main__":
    main()
