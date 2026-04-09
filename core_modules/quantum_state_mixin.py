"""Quantum State Management mixin for EchoesAssistantV2.

Extracted from assistant_v2_core.py (lines 2593–2750) as part of the
god-module decomposition.  All methods operate on ``self.quantum_state_manager``
which is initialised by the host class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from misc.quantum_state.quantum_state_manager import QuantumStateManager


class QuantumStateMixin:
    """Quantum state CRUD, transitions, persistence and metrics."""

    # -- Attribute stubs for type checkers (set by the host class) -----------
    quantum_state_manager: QuantumStateManager

    # -- Public API ----------------------------------------------------------

    def update_quantum_state(self, key: str, value: Any, entangle_with: list[str] = None) -> dict[str, Any]:
        """Update a quantum state with optional entanglement.

        Args:
            key: State key to update
            value: New value for the state
            entangle_with: Keys to entangle with this state

        Returns:
            Result with success status and entangled states
        """
        try:
            self.quantum_state_manager.update_state(key, value, entangle_with)
            entangled = self.quantum_state_manager.get_entangled_states(key) if entangle_with else {}
            return {"success": True, "key": key, "value": value, "entangled": entangled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def measure_quantum_state(self, key: str) -> dict[str, Any]:
        """Measure (read) a quantum state.

        Args:
            key: State key to measure

        Returns:
            Result with measured value
        """
        try:
            value = self.quantum_state_manager.measure_state(key)
            return {"success": True, "key": key, "value": value}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_superposition(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple quantum states in superposition.

        Args:
            keys: List of state keys to retrieve

        Returns:
            Result with superposition of states
        """
        try:
            superposition = self.quantum_state_manager.get_superposition(keys)
            return {"success": True, "superposition": superposition}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_entangled_states(self, key: str) -> dict[str, Any]:
        """Get states entangled with the given key.

        Args:
            key: State key to check entanglement for

        Returns:
            Result with entangled states
        """
        try:
            entangled = self.quantum_state_manager.get_entangled_states(key)
            return {"success": True, "key": key, "entangled": entangled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def transition_quantum_state(self) -> dict[str, Any]:
        """Perform a probabilistic quantum state transition.

        Returns:
            Result with new state after transition
        """
        try:
            new_state = self.quantum_state_manager.transition_state()
            return {"success": True, "new_state": new_state}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_state_history(self, key: str) -> dict[str, Any]:
        """Get historical values for a quantum state.

        Args:
            key: State key to get history for

        Returns:
            Result with state history
        """
        try:
            history = self.quantum_state_manager.get_state_history(key)
            return {"success": True, "key": key, "history": history}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_quantum_metrics(self) -> dict[str, Any]:
        """Get quantum state management performance metrics.

        Returns:
            Result with performance metrics
        """
        try:
            metrics = self.quantum_state_manager.get_metrics()
            return {
                "success": True,
                "metrics": {
                    "total_updates": metrics.total_updates,
                    "total_measurements": metrics.total_measurements,
                    "average_transition_time": metrics.average_transition_time,
                    "entangled_states_count": metrics.entangled_states_count,
                    "last_updated": (metrics.last_updated.isoformat() if metrics.last_updated else None),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_quantum_state(self, filepath: str = "quantum_state_backup.json") -> dict[str, Any]:
        """Save the current quantum state to a file.

        Args:
            filepath: Path to save the state file

        Returns:
            Result with save status
        """
        try:
            # Import here to avoid circular dependency at module level
            from misc.quantum_state.quantum_state_manager import QuantumStateManager as _QSM

            # Create a temporary quantum state manager with persistence
            temp_qsm = _QSM(persistence_file=filepath)
            # Copy current state
            temp_qsm.quantum_state._state = self.quantum_state_manager.quantum_state._state.copy()
            temp_qsm.quantum_state._entangled = self.quantum_state_manager.quantum_state._entangled.copy()
            temp_qsm.quantum_state._history = self.quantum_state_manager.quantum_state._history.copy()
            temp_qsm.state_machine = self.quantum_state_manager.state_machine
            temp_qsm.metrics = self.quantum_state_manager.metrics
            temp_qsm.interference_patterns = self.quantum_state_manager.interference_patterns.copy()

            temp_qsm.save_state()
            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_quantum_state(self, filepath: str = "quantum_state_backup.json") -> dict[str, Any]:
        """Load quantum state from a file.

        Args:
            filepath: Path to the state file

        Returns:
            Result with load status
        """
        try:
            from misc.quantum_state.quantum_state_manager import QuantumStateManager as _QSM

            temp_qsm = _QSM(persistence_file=filepath)
            temp_qsm.load_state()

            # Copy loaded state to current manager
            self.quantum_state_manager.quantum_state._state = temp_qsm.quantum_state._state.copy()
            self.quantum_state_manager.quantum_state._entangled = temp_qsm.quantum_state._entangled.copy()
            self.quantum_state_manager.quantum_state._history = temp_qsm.quantum_state._history.copy()
            self.quantum_state_manager.state_machine = temp_qsm.state_machine
            self.quantum_state_manager.metrics = temp_qsm.metrics
            self.quantum_state_manager.interference_patterns = temp_qsm.interference_patterns.copy()

            return {"success": True, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}
