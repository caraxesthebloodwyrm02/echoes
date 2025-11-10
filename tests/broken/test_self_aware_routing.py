"""
Unit Tests for Self-Aware Routing System
Comprehensive test suite covering all components and scenarios.
"""

import asyncio
import pytest
import pytest_asyncio
import time

# Import the modules to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.routing.self_aware_routing import (
    SelfAwareRouter,
    Component,
    SystemStatus,
    IssueType,
    RepairAction
)


class TestComponent:
    """Test the Component dataclass."""
    
    def test_component_creation(self):
        """Test creating a component."""
        comp = Component(
            id="test",
            endpoint="https://test.com",
            priority=5,
            max_concurrent=20
        )
        
        assert comp.id == "test"
        assert comp.endpoint == "https://test.com"
        assert comp.priority == 5
        assert comp.max_concurrent == 20
        assert comp.is_active
        assert comp.health_score == 1.0
        assert comp.is_healthy
    
    def test_component_health_check(self):
        """Test component health evaluation."""
        # Healthy component
        comp1 = Component(id="healthy", endpoint="https://test.com")
        assert comp1.is_healthy
        
        # Unhealthy due to low health score
        comp2 = Component(id="unhealthy", endpoint="https://test.com", health_score=0.3)
        assert not comp2.is_healthy
        
        # Unhealthy due to failures
        comp3 = Component(id="failed", endpoint="https://test.com", failure_count=5)
        assert not comp3.is_healthy
        
        # Inactive component
        comp4 = Component(id="inactive", endpoint="https://test.com", is_active=False)
        assert not comp4.is_healthy


class TestSelfAwareRouter:
    """Test the SelfAwareRouter class."""
    
    @pytest_asyncio.fixture
    async def router(self):
        """Create a router for testing."""
        router = SelfAwareRouter(health_check_interval=0.1)  # Fast for testing
        await router.start()
        yield router
        await router.stop()
    
    @pytest.fixture
    def sample_components(self):
        """Create sample components for testing."""
        return [
            Component(id="comp1", endpoint="https://api1.com", priority=3, max_concurrent=10),
            Component(id="comp2", endpoint="https://api2.com", priority=2, max_concurrent=5),
            Component(id="comp3", endpoint="https://api3.com", priority=1, max_concurrent=20)
        ]
    
    @pytest.mark.asyncio
    async def test_router_initialization(self):
        """Test router initialization."""
        router = SelfAwareRouter()
        assert router.health_check_interval == 5.0
        assert router.system_status == SystemStatus.FLOWING
        assert len(router.components) == 0
        assert len(router.repair_history) == 0
    
    @pytest.mark.asyncio
    async def test_register_component(self, router, sample_components):
        """Test registering components."""
        for comp in sample_components:
            router.register_component(comp)
        
        assert len(router.components) == 3
        assert "comp1" in router.components
        assert "comp2" in router.components
        assert "comp3" in router.components
    
    @pytest.mark.asyncio
    async def test_route_request_healthy(self, router, sample_components):
        """Test routing requests to healthy components."""
        for comp in sample_components:
            router.register_component(comp)
        
        route = await router.route_request("test request")
        
        assert route.component_id in ["comp1", "comp2", "comp3"]
        assert route.confidence > 0
        assert route.reason is not None
        assert not route.fallback_used
    
    @pytest.mark.asyncio
    async def test_route_request_preferred(self, router, sample_components):
        """Test routing with preferred component."""
        for comp in sample_components:
            router.register_component(comp)
        
        route = await router.route_request("test request", preferred_component="comp2")
        
        assert route.component_id == "comp2"
        assert route.confidence == 0.9
        assert "Preferred" in route.reason
    
    @pytest.mark.asyncio
    async def test_route_request_no_components(self, router):
        """Test routing when no components are available."""
        route = await router.route_request("test request")
        
        assert route.component_id == ""
        assert route.confidence == 0.0
        assert route.fallback_used
    
    @pytest.mark.asyncio
    async def test_health_check(self, router, sample_components):
        """Test health check functionality."""
        for comp in sample_components:
            router.register_component(comp)
        
        # Wait for at least one health check
        await asyncio.sleep(0.2)
        
        # Components should still be healthy
        for comp in router.components.values():
            assert comp.is_healthy
            assert comp.last_check > 0
    
    @pytest.mark.asyncio
    async def test_component_failure_detection(self, router, sample_components):
        """Test detection of component failures."""
        for comp in sample_components:
            router.register_component(comp)
        
        # Simulate a failure
        router.components["comp2"].failure_count = 5
        router.components["comp2"].health_score = 0.2
        
        # Route should avoid failed component
        route = await router.route_request("test request")
        assert route.component_id != "comp2"
    
    @pytest.mark.asyncio
    async def test_congestion_detection(self, router, sample_components):
        """Test congestion detection and handling."""
        for comp in sample_components:
            router.register_component(comp)
        
        # Simulate high load
        for i in range(50):  # More than total capacity
            router.active_requests[f"req_{i}"] = time.time()
        
        # Wait for detection
        await asyncio.sleep(0.2)
        
        # Check if congestion was detected
        congestion_repairs = [
            r for r in router.repair_history 
            if r.issue_type == IssueType.CONGESTION
        ]
        assert len(congestion_repairs) > 0
    
    @pytest.mark.asyncio
    async def test_timeout_detection(self, router, sample_components):
        """Test timeout detection and cleanup."""
        for comp in sample_components:
            router.register_component(comp)
        
        # Simulate stuck requests
        old_time = time.time() - 35  # 35 seconds ago
        router.active_requests["stuck1"] = old_time
        router.active_requests["stuck2"] = old_time
        
        # Wait for detection
        await asyncio.sleep(0.2)
        
        # Stuck requests should be cleaned up
        assert "stuck1" not in router.active_requests
        assert "stuck2" not in router.active_requests
        
        # Should have repair actions
        timeout_repairs = [
            r for r in router.repair_history 
            if r.issue_type == IssueType.TIMEOUT
        ]
        assert len(timeout_repairs) > 0
    
    @pytest.mark.asyncio
    async def test_status_updates(self, router, sample_components):
        """Test system status updates."""
        for comp in sample_components:
            router.register_component(comp)
        
        # Initially should be flowing
        assert router.system_status == SystemStatus.FLOWING
        
        # Simulate some failures
        router.components["comp2"].failure_count = 3
        router.components["comp2"].health_score = 0.3
        
        # Wait for status update
        await asyncio.sleep(0.2)
        
        # Status should reflect issues
        assert router.system_status != SystemStatus.FLOWING
    
    @pytest.mark.asyncio
    async def test_get_status_message(self):
        """Test getting friendly status messages."""
        router = SelfAwareRouter()
        router.system_status = SystemStatus.FLOWING
        msg = router.get_status_message()
        assert "✨" in msg or "🌟" in msg or "💫" in msg
        
        router.system_status = SystemStatus.REPAIRING
        msg = router.get_status_message()
        assert "🔧" in msg or "🛠️" in msg or "⚡" in msg
    
    @pytest.mark.asyncio
    async def test_get_metrics(self):
        """Test getting system metrics."""
        router = SelfAwareRouter()
        sample_components = [
            Component(id="comp1", endpoint="https://api1.com", priority=3, max_concurrent=10),
            Component(id="comp2", endpoint="https://api2.com", priority=2, max_concurrent=5),
            Component(id="comp3", endpoint="https://api3.com", priority=1, max_concurrent=20)
        ]
        for comp in sample_components:
            router.register_component(comp)
        
        metrics = router.get_metrics()
        
        assert "system_status" in metrics
        assert "status_message" in metrics
        assert "components" in metrics
        assert metrics["components"]["total"] == 3
        assert metrics["components"]["healthy"] == 3
    
    @pytest.mark.asyncio
    async def test_get_repair_history(self):
        """Test getting repair history."""
        router = SelfAwareRouter()
        # Add some repair actions
        router.repair_history = [
            RepairAction(
                timestamp=time.time(),
                component_id="test",
                issue_type=IssueType.TIMEOUT,
                action="test action",
                success=True,
                message="test message"
            )
        ]
        
        history = router.get_repair_history(5)
        assert len(history) == 1
        assert history[0]["component"] == "test"
        assert history[0]["issue"] == "timeout"
    
    @pytest.mark.asyncio
    async def test_record_request_lifecycle(self, router, sample_components):
        """Test recording request start and end."""
        for comp in sample_components:
            router.register_component(comp)
        
        request_id = "test_req"
        
        # Record start
        await router.record_request_start(request_id)
        assert request_id in router.active_requests
        
        # Record end
        await router.record_request_end(request_id, "comp1", True, 0.5)
        assert request_id not in router.active_requests
        assert len(router.response_times) == 1
        assert router.response_times[0] == 0.5
        
        # Component should have improved health
        comp1 = router.components["comp1"]
        assert comp1.success_count == 1
        assert comp1.health_score > 1.0  # Should be >1 due to improvement


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test the complete lifecycle of the routing system."""
        router = SelfAwareRouter(health_check_interval=0.1)
        
        # Register components
        router.register_component(Component(id="api1", endpoint="https://api1.com"))
        router.register_component(Component(id="api2", endpoint="https://api2.com"))
        
        # Start router
        await router.start()
        
        try:
            # Make some requests
            for i in range(5):
                route = await router.route_request(f"request_{i}")
                assert route.component_id in ["api1", "api2"]
                
                # Record request completion
                await router.record_request_start(f"req_{i}")
                await asyncio.sleep(0.01)
                await router.record_request_end(f"req_{i}", route.component_id, True, 0.1)
            
            # Simulate a failure
            router.components["api2"].failure_count = 5
            router.components["api2"].health_score = 0.1
            
            # Next request should avoid failed component
            route = await router.route_request("test_after_failure")
            assert route.component_id == "api1"
            
            # Check metrics
            metrics = router.get_metrics()
            assert metrics["components"]["healthy"] == 1
            assert metrics["active_requests"] == 0
            
        finally:
            await router.stop()
    
    @pytest.mark.asyncio
    async def test_emergency_recovery(self):
        """Test emergency recovery when all components fail."""
        router = SelfAwareRouter(health_check_interval=0.1)
        
        # Register components
        router.register_component(Component(id="api1", endpoint="https://api1.com"))
        router.register_component(Component(id="api2", endpoint="https://api2.com"))
        
        await router.start()
        
        try:
            # Deactivate all components
            for comp in router.components.values():
                comp.is_active = False
            
            # Route request should trigger emergency recovery
            await router.route_request("emergency_test")
            
            # Components should be reactivated
            assert all(comp.is_active for comp in router.components.values())
            
            # Should have emergency repair in history
            emergency_repairs = [
                r for r in router.repair_history 
                if "emergency" in r.message.lower()
            ]
            assert len(emergency_repairs) > 0
            
        finally:
            await router.stop()


# Smoke Tests
class TestSmoke:
    """Smoke tests to ensure basic functionality works."""
    
    @pytest.mark.asyncio
    async def test_smoke_basic_functionality(self):
        """Basic smoke test for core functionality."""
        router = SelfAwareRouter(health_check_interval=0.1)
        
        # Register a component
        router.register_component(Component(id="smoke_test", endpoint="https://test.com"))
        
        # Start the router
        await router.start()
        
        try:
            # Route a request
            route = await router.route_request("smoke request")
            assert route.component_id == "smoke_test"
            
            # Get status
            status = router.get_status_message()
            assert status is not None
            
            # Get metrics
            metrics = router.get_metrics()
            assert metrics["components"]["total"] == 1
            
        finally:
            await router.stop()
    
    @pytest.mark.asyncio
    async def test_smoke_multiple_components(self):
        """Smoke test with multiple components."""
        router = SelfAwareRouter(health_check_interval=0.1)
        
        # Add multiple components
        for i in range(3):
            router.register_component(
                Component(id=f"smoke_{i}", endpoint=f"https://test{i}.com")
            )
        
        await router.start()
        
        try:
            # Make multiple requests
            for i in range(10):
                route = await router.route_request(f"smoke_request_{i}")
                assert route.component_id.startswith("smoke_")
            
        finally:
            await router.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
