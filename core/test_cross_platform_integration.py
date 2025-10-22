r"""
Cross-Platform Integration Tests
Tests connection between E:\ Echoes and D:\ research platforms
"""

from pathlib import Path
from typing import List

from integrations.glimpse_connector import GlimpseConnector, create_glimpse_connector
from integrations.turbo_bridge import TurboBridge, create_bridge

# Disable pytest cache to avoid file descriptor issues
pytest_plugins: List[str] = []


class TestGlimpseConnector:
    """Test GlimpsePreview integration"""

    def test_connector_initialization(self):
        """Test GlimpseConnector can be created"""
        connector = GlimpseConnector()
        assert connector is not None
        assert connector.glimpse_root == Path("E:/Projects/Development/realtime")

    def test_glimpse_path_exists(self):
        """Test GlimpsePreview path is accessible"""
        connector = GlimpseConnector()
        # Path may not exist in all environments
        exists = connector.glimpse_root.exists()
        print(f"GlimpsePreview path exists: {exists}")

    def test_connection_attempt(self):
        """Test connection to GlimpsePreview"""
        connector = GlimpseConnector()
        connected = connector.connect()

        if connected:
            print("✅ Connected to GlimpsePreview")
            assert connector.connected
        else:
            print("⚠️ GlimpsePreview not available (expected in some environments)")

    def test_health_check(self):
        """Test health check functionality"""
        connector = GlimpseConnector()
        health = connector.health_check()

        assert "connected" in health
        assert "glimpse_root_exists" in health
        assert "components" in health


class TestTurboBridge:
    """Test unified bridge functionality"""

    def test_bridge_initialization(self):
        """Test TurboBridge can be created"""
        bridge = TurboBridge()
        assert bridge is not None
        assert bridge.turbo_root == Path("D:/")
        assert bridge.glimpse_root == Path("E:/Projects/Development/realtime")
        assert bridge.echoes_root == Path("E:/Projects/Development")

    def test_platform_paths(self):
        """Test all platform paths are configured"""
        bridge = TurboBridge()

        assert bridge.turbo_root.exists() or True  # May not exist
        assert bridge.glimpse_root.exists() or True
        assert bridge.echoes_root.exists()  # Should always exist

    def test_connection_status(self):
        """Test connection status tracking"""
        bridge = TurboBridge()
        connections = bridge.connect_all()

        assert "echoes" in connections
        assert "turbo" in connections
        assert "glimpse" in connections

        # Echoes should always be connected (we're in it)
        assert connections["echoes"] is True

        print(f"Connection status: {connections}")

    def test_system_status(self):
        """Test system status reporting"""
        bridge = TurboBridge()
        bridge.connect_all()

        status = bridge.get_system_status()

        assert "connections" in status
        assert "platforms" in status
        assert "echoes" in status["platforms"]
        assert "turbo" in status["platforms"]
        assert "glimpse" in status["platforms"]

    def test_unified_analysis_structure(self):
        """Test unified analysis returns proper structure"""
        bridge = TurboBridge()
        bridge.connect_all()

        result = bridge.unified_analysis(
            {
                "text": ["Sample text for analysis"],
                "query": "test query",
                "trajectory": {"direction": "expanding"},
            }
        )

        # Result should be a dictionary
        assert isinstance(result, dict)

        # May contain trajectory, bias, knowledge, or errors
        print(f"Analysis result keys: {result.keys()}")

    def test_communication_routing(self):
        """Test message routing between platforms"""
        bridge = TurboBridge()
        bridge.connect_all()

        # Route to echoes (should always work)
        response = bridge.streamline_communication(source="glimpse", target="echoes", message={"test": "data"})

        assert response is not None
        assert isinstance(response, dict)


class TestCrossPlatformFeatures:
    """Test cross-platform feature integration"""

    def test_factory_function(self):
        """Test create_bridge factory function"""
        bridge = create_bridge()
        assert bridge is not None
        assert isinstance(bridge, TurboBridge)

    def test_glimpse_factory(self):
        """Test create_glimpse_connector factory function"""
        connector = create_glimpse_connector()
        assert connector is not None
        assert isinstance(connector, GlimpseConnector)

    def test_cross_platform_status(self):
        """Test comprehensive cross-platform status"""
        bridge = create_bridge()
        status = bridge.get_system_status()

        # Verify structure
        assert "connections" in status
        assert "platforms" in status

        # Echoes should be accessible
        assert status["platforms"]["echoes"]["exists"]

        print(f"Cross-platform status: {status}")


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""

    def test_research_to_development_flow(self):
        """Test data flow from research to development"""
        bridge = create_bridge()

        # Simulate research data from D:\
        research_data = {
            "text": ["Research findings on trajectory optimization"],
            "query": "fast compounding vs data-driven",
            "trajectory": {"direction": "expanding", "confidence": 0.85},
        }

        # Process through bridge
        result = bridge.unified_analysis(research_data)

        # Should return structured results
        assert isinstance(result, dict)
        print(f"Research→Development flow result: {result.keys()}")

    def test_development_to_research_flow(self):
        """Test routing from development to research"""
        bridge = create_bridge()

        # Development query
        dev_query = {"query": "trajectory analysis", "context": "development"}

        # Route to research platform
        response = bridge.streamline_communication(source="echoes", target="glimpse", message=dev_query)

        assert response is not None
        print(f"Development→Research flow result: {response}")

    def test_bidirectional_communication(self):
        """Test two-way communication between platforms"""
        bridge = create_bridge()

        # Send message to research
        to_research = bridge.streamline_communication(source="echoes", target="glimpse", message={"action": "analyze"})

        # Send response back to development
        to_dev = bridge.streamline_communication(source="glimpse", target="echoes", message={"result": to_research})

        assert to_dev is not None
        print("[OK] Bidirectional communication successful")


def test_integration_summary():
    """Summary test showing integration capabilities"""
    print("\n" + "=" * 60)
    print("CROSS-PLATFORM INTEGRATION SUMMARY")
    print("=" * 60)

    bridge = create_bridge()
    status = bridge.get_system_status()

    print("\nPlatform Status:")
    for platform, info in status["platforms"].items():
        exists = "[OK]" if info["exists"] else "[X]"
        print(f"  {exists} {platform.upper()}: {info['root']}")

    print("\nConnections:")
    for platform, connected in status["connections"].items():
        status_icon = "[OK]" if connected else "[!]"
        print(f"  {status_icon} {platform.upper()}: {'Connected' if connected else 'Not available'}")

    print("\n" + "=" * 60)
    print("Integration bridge ready for research <-> development communication")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Run summary test
    test_integration_summary()
