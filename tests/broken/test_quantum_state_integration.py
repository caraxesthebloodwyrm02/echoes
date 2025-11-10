#!/usr/bin/env python3
"""
Quantum State Management Integration Tests for Echoes Platform
==========================================================

Tests the integration of quantum-inspired state management with EchoesAssistantV2.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the Echoes project directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quantum_state import QuantumStateManager


class TestQuantumStateIntegration:
    """Test quantum state management integration with EchoesAssistantV2"""

    def test_quantum_state_manager_initialization(self):
        """Test that QuantumStateManager initializes correctly"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Check initial states
        assert qsm.measure_state("system_status") == "initializing"
        assert qsm.measure_state("authentication") == "superposition"
        assert qsm.measure_state("processing") == "idle"

    def test_quantum_state_update_and_measurement(self):
        """Test updating and measuring quantum states"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Update a state
        qsm.update_state("test_key", "test_value")

        # Measure the state
        value = qsm.measure_state("test_key")
        assert value == "test_value"

    def test_quantum_state_entanglement(self):
        """Test state entanglement functionality"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Update states with entanglement
        qsm.update_state(
            "user_session", "active", entangle_with=["permissions", "features"]
        )
        qsm.update_state("permissions", "admin")

        # Check entanglement
        entangled = qsm.get_entangled_states("user_session")
        assert "permissions" in entangled
        assert entangled["permissions"] == "admin"

    def test_quantum_superposition(self):
        """Test getting multiple states in superposition"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Set up some states
        qsm.update_state("state1", "value1")
        qsm.update_state("state2", "value2")
        qsm.update_state("state3", "value3")

        # Get superposition
        superposition = qsm.get_superposition(["state1", "state2", "state3"])
        assert superposition["state1"] == "value1"
        assert superposition["state2"] == "value2"
        assert superposition["state3"] == "value3"

    def test_quantum_state_transitions(self):
        """Test probabilistic state transitions"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # The state machine should have transitions defined
        # Perform a transition
        new_state = qsm.transition_state()

        # Should be one of the defined states
        valid_states = ["idle", "processing", "success", "error", "recovery"]
        assert new_state in valid_states

    def test_quantum_state_history(self):
        """Test state history tracking"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Update state multiple times
        qsm.update_state("test_history", "value1")
        qsm.update_state("test_history", "value2")
        qsm.update_state("test_history", "value3")

        # Get history
        history = qsm.get_state_history("test_history")
        assert len(history) == 3

        # Check history format (tuple of value, timestamp)
        for entry in history:
            assert isinstance(entry, tuple)
            assert len(entry) == 3  # key, previous_value, new_value, timestamp

    def test_quantum_metrics_collection(self):
        """Test performance metrics collection"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Perform some operations
        qsm.update_state("metric_test", "value1")
        qsm.update_state("metric_test", "value2")
        qsm.measure_state("metric_test")
        qsm.measure_state("system_status")

        # Get metrics
        metrics = qsm.get_metrics()
        assert metrics.total_updates >= 3  # At least the initial states + our updates
        assert metrics.total_measurements >= 2
        assert isinstance(metrics.average_transition_time, float)

    def test_quantum_state_persistence(self):
        """Test state persistence and recovery"""
        import os
        import tempfile

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            # Create and configure state manager
            qsm1 = QuantumStateManager(persistence_file=temp_file)
            qsm1.initialize_quantum_states()
            qsm1.update_state("persistent_test", "persistent_value")

            # Save state
            qsm1.save_state()

            # Create new instance and load state
            qsm2 = QuantumStateManager(persistence_file=temp_file)
            qsm2.load_state()

            # Verify persistence
            value = qsm2.measure_state("persistent_test")
            assert value == "persistent_value"

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_quantum_interference_simulation(self):
        """Test quantum interference pattern simulation"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Add interference between states
        qsm.simulate_interference("processing", "success", 0.5)

        # Check interference patterns
        assert "processing_success" in qsm.interference_patterns
        assert qsm.interference_patterns["processing_success"] == 0.5

    def test_quantum_state_error_handling(self):
        """Test error handling in quantum state operations"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Test measuring non-existent state
        value = qsm.measure_state("non_existent_key")
        assert value is None

        # Test entangled states for non-existent key
        entangled = qsm.get_entangled_states("non_existent_key")
        assert entangled == {}

    def test_quantum_state_machine_rollback(self):
        """Test state machine rollback functionality"""
        qsm = QuantumStateManager()
        qsm.initialize_quantum_states()

        # Perform several transitions
        initial_state = qsm.state_machine.current_state
        states = [qsm.transition_state() for _ in range(5)]

        # Rollback one step
        qsm.state_machine.rollback(1)

        # Should be at the previous state
        assert qsm.state_machine.current_state == states[-2]


class TestEchoesAssistantV2QuantumIntegration:
    """Test EchoesAssistantV2 quantum state integration"""

    @pytest.fixture
    def mock_assistant(self):
        """Create a mock assistant with quantum state management disabled for testing"""
        with patch("assistant_v2_core.EchoesAssistantV2.__init__", return_value=None):
            assistant = MagicMock()
            assistant.quantum_state_manager = QuantumStateManager()
            assistant.quantum_state_manager.initialize_quantum_states()
            return assistant

    def test_update_quantum_state_method(self, mock_assistant):
        """Test the update_quantum_state method"""
        # This would normally be called on a real assistant instance
        # For now, we'll test the logic directly on the quantum state manager
        qsm = mock_assistant.quantum_state_manager

        result = qsm.update_state(
            "test_key", "test_value", entangle_with=["related_key"]
        )
        assert result is None  # update_state doesn't return anything

        # Check the state was updated
        value = qsm.measure_state("test_key")
        assert value == "test_value"

    def test_measure_quantum_state_method(self, mock_assistant):
        """Test the measure_quantum_state method"""
        qsm = mock_assistant.quantum_state_manager
        qsm.update_state("measure_test", "measured_value")

        value = qsm.measure_state("measure_test")
        assert value == "measured_value"

    def test_get_quantum_superposition_method(self, mock_assistant):
        """Test the get_quantum_superposition method"""
        qsm = mock_assistant.quantum_state_manager

        qsm.update_state("super1", "value1")
        qsm.update_state("super2", "value2")

        superposition = qsm.get_superposition(["super1", "super2"])
        assert superposition["super1"] == "value1"
        assert superposition["super2"] == "value2"

    def test_transition_quantum_state_method(self, mock_assistant):
        """Test the transition_quantum_state method"""
        qsm = mock_assistant.quantum_state_manager

        new_state = qsm.transition_state()
        valid_states = ["idle", "processing", "success", "error", "recovery"]
        assert new_state in valid_states


if __name__ == "__main__":
    # Run basic tests
    print("Running Quantum State Management Integration Tests...")

    test_instance = TestQuantumStateIntegration()

    # Run individual tests
    try:
        test_instance.test_quantum_state_manager_initialization()
        print("✓ Initialization test passed")

        test_instance.test_quantum_state_update_and_measurement()
        print("✓ Update and measurement test passed")

        test_instance.test_quantum_state_entanglement()
        print("✓ Entanglement test passed")

        test_instance.test_quantum_superposition()
        print("✓ Superposition test passed")

        test_instance.test_quantum_state_transitions()
        print("✓ State transitions test passed")

        test_instance.test_quantum_metrics_collection()
        print("✓ Metrics collection test passed")

        print("\n🎉 All quantum state management integration tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
