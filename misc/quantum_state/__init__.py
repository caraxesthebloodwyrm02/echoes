"""
Quantum-Inspired State Management System
========================================

A Python library implementing quantum computing concepts for classical state management.

Modules:
- quantum_state: Core quantum state representation with superposition and entanglement
- quantum_state_machine: Probabilistic state transitions
- quantum_state_manager: Unified interface for state management

Key Features:
- Superposition: States can exist in multiple configurations
- Entanglement: Related states update together
- Probabilistic Transitions: Uncertainty in state changes
- Observer Pattern: Reactive state management
- Persistence: State serialization and recovery
- Performance Monitoring: Metrics and analytics

Usage:
    from quantum_state import QuantumStateManager

    qsm = QuantumStateManager()
    qsm.initialize_quantum_states()
    qsm.update_state('my_state', 'value', entangle_with=['related_state'])
"""

from .quantum_state import QuantumState, QuantumStateError
from .quantum_state_machine import QuantumStateMachine
from .quantum_state_manager import QuantumStateManager, StateMetrics

__version__ = "1.0.0"
__author__ = "Cascade AI Assistant"
__license__ = "MIT"

__all__ = [
    "QuantumState",
    "QuantumStateError",
    "QuantumStateMachine",
    "QuantumStateManager",
    "StateMetrics",
]
