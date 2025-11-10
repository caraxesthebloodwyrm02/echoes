"""
Tests for ecosystem-inspired resilience patterns in Echoes platform.
Tests include HerdImmunityRateLimiter, SymbioticService, HibernationManager,
SchoolingLoadBalancer, and DecoySystem implementations.
"""

import time
from unittest.mock import Mock, patch

import pytest

# Import the ecosystem components
from automation.ecosystem_resilience import (
    DecoySystem,
    HerdImmunityRateLimiter,
    HibernationManager,
    SchoolingLoadBalancer,
    SymbioticService,
)


class TestHerdImmunityRateLimiter:
    """Test suite for HerdImmunityRateLimiter class."""

    def test_initialization(self):
        """Test proper initialization of the rate limiter."""
        limiter = HerdImmunityRateLimiter(base_rate=100, herd_immunity_threshold=0.7)
        assert limiter.base_rate == 100
        assert limiter.herd_immunity_threshold == 0.7
        assert limiter.healthy_instances == []
        assert limiter.total_instances == 0

    def test_full_capacity_when_all_healthy(self):
        """Test that full capacity is maintained when all instances are healthy."""
        limiter = HerdImmunityRateLimiter(base_rate=100, herd_immunity_threshold=0.7)
        limiter.total_instances = 5

        # Mark all instances as healthy
        for i in range(5):
            limiter.update_health_status(f"instance_{i}", True)

        effective_rate = limiter.get_effective_rate_limit()
        assert effective_rate == 100  # Full capacity

    def test_reduced_capacity_below_threshold(self):
        """Test rate reduction when healthy ratio falls below threshold."""
        limiter = HerdImmunityRateLimiter(base_rate=100, herd_immunity_threshold=0.7)
        limiter.total_instances = 5

        # Mark only 2 out of 5 instances as healthy (40% < 70% threshold)
        for i in range(2):
            limiter.update_health_status(f"instance_{i}", True)

        effective_rate = limiter.get_effective_rate_limit()
        assert effective_rate < 100  # Should be reduced
        # Expected: 100 * (0.4 / 0.7) = ~57
        assert 55 <= effective_rate <= 60

    def test_exact_threshold_boundary(self):
        """Test behavior exactly at the threshold boundary."""
        limiter = HerdImmunityRateLimiter(base_rate=100, herd_immunity_threshold=0.7)
        limiter.total_instances = 10

        # Mark exactly 7 instances as healthy (70% = threshold)
        for i in range(7):
            limiter.update_health_status(f"instance_{i}", True)

        effective_rate = limiter.get_effective_rate_limit()
        assert effective_rate == 100  # Should be full capacity at threshold

    def test_instance_health_updates(self):
        """Test that instance health status updates correctly."""
        limiter = HerdImmunityRateLimiter()
        limiter.total_instances = 3

        # Add healthy instance
        limiter.update_health_status("instance_1", True)
        assert "instance_1" in limiter.healthy_instances
        assert len(limiter.healthy_instances) == 1

        # Mark instance as unhealthy
        limiter.update_health_status("instance_1", False)
        assert "instance_1" not in limiter.healthy_instances
        assert len(limiter.healthy_instances) == 0


class TestSymbioticService:
    """Test suite for SymbioticService class."""

    def test_initialization(self):
        """Test proper initialization of symbiotic service."""
        service = SymbioticService()
        assert service.partners == {}
        assert service.resources == {}

    def test_partner_registration(self):
        """Test registration of partner services."""
        service = SymbioticService()

        def mock_benefit(resource):
            return f"benefit_{resource}"

        def mock_cost(resource):
            return f"cost_{resource}"

        service.register_partner("test_service", mock_benefit, mock_cost)

        assert "test_service" in service.partners
        assert service.partners["test_service"]["benefit"] == mock_benefit
        assert service.partners["test_service"]["cost"] == mock_cost

    def test_resource_request_success(self):
        """Test successful resource request from partner."""
        service = SymbioticService()
        service.add_resource("test_resource", "test_data", 5)

        def mock_benefit(resource):
            return "benefit"

        def mock_cost(resource):
            return 10

        service.register_partner("partner_service", mock_benefit, mock_cost)

        result = service.request_resource("test_resource", "partner_service")

        assert result is not None
        assert result["resource"] == "test_resource"
        assert result["data"] == "test_data"
        assert result["cost"] == 10
        assert service.resources["test_resource"]["available"] == 4

    def test_resource_request_no_partner(self):
        """Test resource request from non-registered partner."""
        service = SymbioticService()

        with pytest.raises(ValueError, match="No symbiotic relationship"):
            service.request_resource("test_resource", "unknown_service")

    def test_resource_request_unavailable(self):
        """Test resource request when resource is unavailable."""
        service = SymbioticService()
        service.resources = {"test_resource": {"available": 0, "data": "test_data"}}

        def mock_benefit(resource):
            return "benefit"

        def mock_cost(resource):
            return 10

        service.register_partner("partner_service", mock_benefit, mock_cost)

        result = service.request_resource("test_resource", "partner_service")
        assert result is None


class TestHibernationManager:
    """Test suite for HibernationManager class."""

    def test_initialization(self):
        """Test proper initialization of hibernation manager."""
        manager = HibernationManager(min_utilization=0.2, max_inactivity=3600)
        assert manager.min_utilization == 0.2
        assert manager.max_inactivity == 3600
        assert not manager.hibernating

    def test_activity_logging(self):
        """Test that activity is logged correctly."""
        manager = HibernationManager()

        # Start in hibernation
        manager.hibernating = True

        # Log activity
        manager.log_activity()

        # Should wake up
        assert not manager.hibernating

    @patch("time.time")
    def test_hibernation_trigger(self, mock_time):
        """Test that hibernation is triggered under correct conditions."""
        manager = HibernationManager(min_utilization=0.2, max_inactivity=3600)

        # Set up conditions for hibernation
        mock_time.return_value = 1000.0
        manager.last_activity = 1000.0 - 4000  # 4000 seconds ago (> 3600)

        with patch.object(manager, "_initiate_hibernation") as mock_hibernate:
            manager.check_hibernation(0.1)  # 10% utilization (< 20% threshold)
            mock_hibernate.assert_called_once()

    @patch("time.time")
    def test_no_hibernation_when_active(self, mock_time):
        """Test that hibernation is not triggered when system is active."""
        manager = HibernationManager(min_utilization=0.2, max_inactivity=3600)

        # Set up conditions that should NOT trigger hibernation
        mock_time.return_value = 1000.0
        manager.last_activity = 1000.0 - 1000  # Only 1000 seconds ago (< 3600)

        with patch.object(manager, "_initiate_hibernation") as mock_hibernate:
            manager.check_hibernation(
                0.1
            )  # Low utilization but not inactive long enough
            mock_hibernate.assert_not_called()

    def test_no_hibernation_when_utilized(self):
        """Test that hibernation is not triggered when utilization is high."""
        manager = HibernationManager(min_utilization=0.2, max_inactivity=3600)

        # Set up conditions with high utilization
        with patch("time.time", return_value=1000.0):
            manager.last_activity = 1000.0 - 4000  # Inactive for long time

            with patch.object(manager, "_initiate_hibernation") as mock_hibernate:
                manager.check_hibernation(0.5)  # 50% utilization (> 20% threshold)
                mock_hibernate.assert_not_called()


class TestSchoolingLoadBalancer:
    """Test suite for SchoolingLoadBalancer class."""

    def test_initialization(self):
        """Test proper initialization of load balancer."""
        nodes = [Mock() for _ in range(3)]
        balancer = SchoolingLoadBalancer(nodes)
        assert balancer.nodes == nodes
        assert balancer.coordination_threshold == 0.7

    def test_single_node_selection(self):
        """Test that single node is always selected."""
        node = Mock()
        balancer = SchoolingLoadBalancer([node])

        result = balancer.get_target_node(Mock())
        assert result == node

    def test_fallback_selection(self):
        """Test fallback to random selection when no coordination."""
        nodes = [Mock() for _ in range(3)]
        balancer = SchoolingLoadBalancer(nodes)
        balancer.last_direction = "unknown"

        # Mock position attribute for nodes
        for i, node in enumerate(nodes):
            node.position = [i, i]
            # Mock the get_load method to return numeric values
            node.get_load.return_value = 0.5

        # Mock the least_loaded selection
        with patch.object(balancer, "_select_node_by_direction") as mock_select:
            mock_select.return_value = nodes[1]
            result = balancer.get_target_node(Mock())
            assert result == nodes[1]

    def test_coordination_needed(self):
        """Test detection of load imbalance requiring coordination."""
        nodes = [Mock() for _ in range(3)]
        balancer = SchoolingLoadBalancer(nodes)

        # Set up uneven loads
        nodes[0].get_load.return_value = 0.9
        nodes[1].get_load.return_value = 0.8
        nodes[2].get_load.return_value = 0.1

        assert balancer._needs_coordination()

    def test_no_coordination_needed(self):
        """Test that balanced loads don't require coordination."""
        nodes = [Mock() for _ in range(3)]
        balancer = SchoolingLoadBalancer(nodes)

        # Set up balanced loads
        nodes[0].get_load.return_value = 0.5
        nodes[1].get_load.return_value = 0.6
        nodes[2].get_load.return_value = 0.4

        assert not balancer._needs_coordination()


class TestDecoySystem:
    """Test suite for DecoySystem class."""

    def test_initialization(self):
        """Test proper initialization of decoy system."""
        system = DecoySystem()
        assert system.decoys == {}
        assert system.attack_patterns == {}

    def test_decoy_creation(self):
        """Test creation of decoy targets."""
        system = DecoySystem()

        decoy_id = system.create_decoy("high_value", "dmz")

        assert decoy_id.startswith("decoy_")
        assert decoy_id in system.decoys
        assert system.decoys[decoy_id]["type"] == "high_value"
        assert system.decoys[decoy_id]["location"] == "dmz"
        assert system.decoys[decoy_id]["interactions"] == 0

    def test_interaction_monitoring(self):
        """Test monitoring of interactions with decoys."""
        system = DecoySystem()
        decoy_id = system.create_decoy("high_value", "dmz")

        result = system.monitor_interaction(decoy_id, "scan", "192.168.1.100")

        assert result
        assert system.decoys[decoy_id]["interactions"] == 1
        assert "scan_192.168.1.100" in system.attack_patterns
        assert system.attack_patterns["scan_192.168.1.100"] == 1

    def test_interaction_with_unknown_decoy(self):
        """Test interaction monitoring with unknown decoy ID."""
        system = DecoySystem()

        result = system.monitor_interaction("unknown_decoy", "scan", "192.168.1.100")
        assert not result

    @patch.object(DecoySystem, "_initiate_countermeasures")
    def test_countermeasure_trigger(self, mock_countermeasures):
        """Test that countermeasures are triggered on repeated attacks."""
        system = DecoySystem()
        decoy_id = system.create_decoy("high_value", "dmz")

        # Simulate multiple attacks from same source
        for _ in range(5):  # Assuming THRESHOLD is 3
            system.monitor_interaction(decoy_id, "scan", "192.168.1.100")

        # Countermeasures should be triggered
        mock_countermeasures.assert_called_with("192.168.1.100")


class TestEcosystemIntegration:
    """Test suite for integration of ecosystem components."""

    def test_resilience_pipeline(self):
        """Test that components work together in a resilience pipeline."""
        # Initialize components
        rate_limiter = HerdImmunityRateLimiter(
            base_rate=100, herd_immunity_threshold=0.7
        )
        hibernation_manager = HibernationManager()
        decoy_system = DecoySystem()

        # Simulate system degradation
        rate_limiter.total_instances = 5
        hibernation_manager.last_activity = time.time() - 4000

        # Mark some instances as unhealthy
        for i in range(2):
            rate_limiter.update_health_status(f"instance_{i}", True)

        # Check system responses
        effective_rate = rate_limiter.get_effective_rate_limit()
        assert effective_rate < 100  # Rate limiting kicks in

        hibernation_manager.check_hibernation(0.1)
        # Should consider hibernation based on inactivity and low utilization

        # Create decoy for protection
        decoy_id = decoy_system.create_decoy("api_endpoint", "dmz")
        assert decoy_id is not None

        # Simulate attack
        decoy_system.monitor_interaction(decoy_id, "brute_force", "attacker_ip")
        assert len(decoy_system.attack_patterns) > 0

    def test_resource_efficiency_metrics(self):
        """Test that ecosystem components improve resource efficiency."""
        rate_limiter = HerdImmunityRateLimiter(base_rate=100)
        rate_limiter.total_instances = 10

        # Full health scenario
        for i in range(10):
            rate_limiter.update_health_status(f"instance_{i}", True)
        full_rate = rate_limiter.get_effective_rate_limit()

        # Degraded health scenario
        rate_limiter.healthy_instances = []
        for i in range(3):
            rate_limiter.update_health_status(f"instance_{i}", True)
        degraded_rate = rate_limiter.get_effective_rate_limit()

        # Verify resource conservation
        assert degraded_rate < full_rate
        efficiency_ratio = degraded_rate / full_rate
        assert 0.2 <= efficiency_ratio <= 0.5  # 30% healthy should give ~43% rate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
