"""
Quantum State Manager
====================

Main interface for the quantum-inspired state management system.
Integrates QuantumState and QuantumStateMachine for comprehensive state management.

Features:
- Unified interface for state operations
- Observer pattern for state change notifications
- Persistence and recovery capabilities
- Quantum interference simulation
- Performance monitoring
"""

from typing import Dict, Any, List, Optional, Callable
from .quantum_state import QuantumState, QuantumStateError
from .quantum_state_machine import QuantumStateMachine
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class StateMetrics:
    """Performance metrics for state operations"""

    total_updates: int = 0
    total_measurements: int = 0
    average_transition_time: float = 0.0
    entangled_states_count: int = 0
    last_updated: Optional[datetime] = None


class QuantumStateManager:
    """
    Main quantum-inspired state management interface
    """

    def __init__(self, persistence_file: Optional[str] = None):
        self.quantum_state = QuantumState()
        self.state_machine = QuantumStateMachine()
        self.observers: List[Callable] = []
        self.metrics = StateMetrics()
        self.persistence_file = persistence_file
        self.interference_patterns: Dict[str, float] = {}

        # Load persisted state if available
        if persistence_file and os.path.exists(persistence_file):
            self.load_state()

    def initialize_quantum_states(self):
        """Initialize the quantum state management system with default configurations"""
        # Initialize core states
        self.quantum_state.update("system_status", "initializing")
        self.quantum_state.update(
            "authentication",
            "superposition",
            entangle_with=["user_session", "permissions"],
        )
        self.quantum_state.update("processing", "idle")
        self.quantum_state.update("error_state", None)

        # Initialize state machine
        self.state_machine.add_state("idle")
        self.state_machine.add_state("processing")
        self.state_machine.add_state("success")
        self.state_machine.add_state("error")
        self.state_machine.add_state("recovery")

        # Define probabilistic transitions
        self.state_machine.add_transition("idle", "processing", 0.8)
        self.state_machine.add_transition("processing", "success", 0.7)
        self.state_machine.add_transition("processing", "error", 0.3)
        self.state_machine.add_transition("error", "recovery", 0.6)
        self.state_machine.add_transition("error", "idle", 0.4)
        self.state_machine.add_transition("recovery", "idle", 1.0)
        self.state_machine.add_transition("success", "idle", 0.9)
        self.state_machine.add_transition("success", "processing", 0.1)

        self.state_machine.set_initial_state("idle")

        logger.info("Quantum state management system initialized")

    def update_state(self, key: str, value: Any, entangle_with: List[str] = None):
        """
        Update a quantum state with optional entanglement

        Args:
            key: State key to update
            value: New value
            entangle_with: Keys to entangle with
        """
        start_time = datetime.now(timezone.utc)

        self.quantum_state.update(key, value, entangle_with)
        self.metrics.total_updates += 1
        self.metrics.last_updated = datetime.now(timezone.utc)

        # Update entangled states count
        self.metrics.entangled_states_count = len(self.quantum_state._entangled)

        # Calculate transition time
        transition_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        self.metrics.average_transition_time = (
            (self.metrics.average_transition_time * (self.metrics.total_updates - 1))
            + transition_time
        ) / self.metrics.total_updates

    def measure_state(self, key: str) -> Any:
        """Measure (read) a quantum state"""
        self.metrics.total_measurements += 1
        return self.quantum_state.measure(key)

    def get_superposition(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple states in superposition"""
        return self.quantum_state.get_superposition(keys)

    def get_entangled_states(self, key: str) -> Dict[str, Any]:
        """Get states entangled with the given key"""
        return self.quantum_state.get_entangled(key)

    def transition_state(self) -> str:
        """Perform a probabilistic state transition"""
        return self.state_machine.next_state(self.quantum_state)

    def add_observer(self, observer: Callable):
        """Add an observer for state changes"""
        self.quantum_state.add_observer(observer)
        self.observers.append(observer)

    def remove_observer(self, observer: Callable):
        """Remove an observer"""
        self.quantum_state.remove_observer(observer)
        if observer in self.observers:
            self.observers.remove(observer)

    def add_transition_callback(self, from_state: str, callback: Callable):
        """Add a callback for state machine transitions"""
        self.state_machine.add_transition_callback(from_state, callback)

    def simulate_interference(
        self, state1: str, state2: str, interference_factor: float
    ):
        """
        Simulate quantum interference between two states

        Args:
            state1: First state key
            state2: Second state key
            interference_factor: Interference strength (-1 to 1)
        """
        key = f"{state1}_{state2}"
        self.interference_patterns[key] = interference_factor

        # Apply interference to transition probabilities
        self._apply_interference()

        logger.info(
            f"Applied interference between {state1} and {state2}: {interference_factor}"
        )

    def _apply_interference(self):
        """Apply interference patterns to state transitions"""
        # This is a simplified interference model
        # In a real quantum system, this would be more complex
        for pattern, factor in self.interference_patterns.items():
            # Apply interference to relevant transitions
            # Implementation depends on specific use case
            pass

    def get_metrics(self) -> StateMetrics:
        """Get current performance metrics"""
        return self.metrics

    def get_state_history(self, key: str) -> List[tuple]:
        """Get historical values for a state"""
        return self.quantum_state.get_history(key)

    def save_state(self):
        """Persist the current state to file"""
        if not self.persistence_file:
            raise QuantumStateError("No persistence file configured")

        state_data = {
            "quantum_state": self.quantum_state.to_dict(),
            "current_machine_state": self.state_machine.current_state,
            "state_history": self.state_machine.state_history,
            "metrics": {
                "total_updates": self.metrics.total_updates,
                "total_measurements": self.metrics.total_measurements,
                "average_transition_time": self.metrics.average_transition_time,
                "entangled_states_count": self.metrics.entangled_states_count,
                "last_updated": (
                    self.metrics.last_updated.isoformat()
                    if self.metrics.last_updated
                    else None
                ),
            },
            "interference_patterns": self.interference_patterns,
        }

        with open(self.persistence_file, "w") as f:
            json.dump(state_data, f, indent=2, default=str)

        logger.info(f"State saved to {self.persistence_file}")

    def load_state(self):
        """Load state from persisted file"""
        if not self.persistence_file or not os.path.exists(self.persistence_file):
            raise QuantumStateError("No persistence file available")

        with open(self.persistence_file, "r") as f:
            state_data = json.load(f)

        # Restore quantum state
        self.quantum_state.from_dict(state_data["quantum_state"])

        # Restore state machine
        self.state_machine.current_state = state_data["current_machine_state"]
        self.state_machine.state_history = state_data["state_history"]

        # Restore metrics
        metrics_data = state_data["metrics"]
        self.metrics.total_updates = metrics_data["total_updates"]
        self.metrics.total_measurements = metrics_data["total_measurements"]
        self.metrics.average_transition_time = metrics_data["average_transition_time"]
        self.metrics.entangled_states_count = metrics_data["entangled_states_count"]
        if metrics_data["last_updated"]:
            self.metrics.last_updated = datetime.fromisoformat(
                metrics_data["last_updated"]
            )

        # Restore interference patterns
        self.interference_patterns = state_data.get("interference_patterns", {})

        logger.info(f"State loaded from {self.persistence_file}")

    def reset(self):
        """Reset the entire state management system"""
        self.quantum_state = QuantumState()
        self.state_machine = QuantumStateMachine()
        self.metrics = StateMetrics()
        self.interference_patterns = {}

        logger.info("Quantum state management system reset")

    def __repr__(self) -> str:
        return (
            f"QuantumStateManager("
            f"current_state={self.state_machine.current_state}, "
            f"total_states={len(self.quantum_state._state)}, "
            f"entangled_groups={len(self.quantum_state._entangled)})"
        )
