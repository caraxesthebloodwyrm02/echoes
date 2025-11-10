"""
Quantum-Inspired State Management System
========================================

This module implements a quantum-inspired state management system that draws parallels
with quantum computing concepts like superposition, entanglement, and state measurement.

Key Concepts:
- Superposition: States can exist in multiple configurations simultaneously
- Entanglement: Related states update together and maintain correlation
- Measurement: Accessing a state value collapses it to a definitive value
- Probabilistic Transitions: State changes can have probability distributions

Author: Cascade AI Assistant
Date: October 2025
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import numpy as np
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantumStateError(Exception):
    """Custom exception for quantum state management errors"""

    pass


@dataclass
class StateTransition:
    """Represents a probabilistic transition between states"""

    from_state: str
    to_state: str
    probability: float
    conditions: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not 0 <= self.probability <= 1:
            raise ValueError("Probability must be between 0 and 1")


class QuantumState:
    """
    Core quantum state representation with superposition and entanglement capabilities
    """

    def __init__(self, initial_state: Dict[str, Any] = None):
        self._state: Dict[str, Any] = initial_state or {}
        self._entangled: Dict[str, List[str]] = {}
        self._history: List[tuple] = []
        self._observers: List[Callable] = []

    def update(self, key: str, value: Any, entangle_with: List[str] = None):
        """
        Update a state value with optional entanglement

        Args:
            key: State key to update
            value: New value for the state
            entangle_with: List of keys to entangle with this state
        """
        previous = self._state.get(key)

        # Update the state
        self._state[key] = value
        self._history.append((key, previous, value, datetime.now(timezone.utc)))

        # Handle entanglement
        if entangle_with:
            self._entangled[key] = self._entangled.get(key, []) + entangle_with
            # Ensure bidirectional entanglement
            for other_key in entangle_with:
                if key not in self._entangled.get(other_key, []):
                    self._entangled[other_key] = self._entangled.get(other_key, []) + [
                        key
                    ]

        # Notify observers
        self._notify_observers(key, previous, value)

        logger.info(f"State updated: {key} = {value}")

    def measure(self, key: str) -> Any:
        """
        Measure a state value (quantum measurement analogy)

        Args:
            key: State key to measure

        Returns:
            Current value of the state
        """
        return self._state.get(key)

    def get_entangled(self, key: str) -> Dict[str, Any]:
        """
        Get all states entangled with the given key

        Args:
            key: State key to check entanglement for

        Returns:
            Dictionary of entangled state values
        """
        entangled_keys = self._entangled.get(key, [])
        return {k: self._state.get(k) for k in entangled_keys}

    def get_superposition(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple states in a single operation (superposition measurement)

        Args:
            keys: List of state keys to retrieve

        Returns:
            Dictionary of state values
        """
        return {k: self._state.get(k) for k in keys}

    def get_history(self, key: str) -> List[tuple]:
        """
        Get historical values for a state

        Args:
            key: State key to get history for

        Returns:
            List of (value, timestamp) tuples
        """
        return [(val, ts) for k, prev, val, ts in self._history if k == key]

    def add_observer(self, observer: Callable):
        """Add an observer for state changes"""
        self._observers.append(observer)

    def remove_observer(self, observer: Callable):
        """Remove an observer"""
        self._observers.remove(observer)

    def _notify_observers(self, key: str, old_val: Any, new_val: Any):
        """Notify all observers of state changes"""
        for observer in self._observers:
            try:
                observer(key, old_val, new_val)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary"""
        return {
            "state": self._state,
            "entangled": self._entangled,
            "history_length": len(self._history),
        }

    def from_dict(self, data: Dict[str, Any]):
        """Deserialize state from dictionary"""
        self._state = data.get("state", {})
        self._entangled = data.get("entangled", {})
