"""
Quantum State Machine
====================

Implements a probabilistic state machine inspired by quantum state transitions.
Supports conditional transitions and interference patterns.

Key Features:
- Probabilistic state transitions
- Conditional transitions based on current state
- Interference patterns for complex state interactions
- State history and rollback capabilities
"""

from typing import Dict, Any, List, Optional, Callable
from .quantum_state import QuantumState, StateTransition
import numpy as np
import logging

logger = logging.getLogger(__name__)


class QuantumStateMachine:
    """
    Probabilistic state machine with quantum-inspired transitions
    """

    def __init__(self):
        self.states = set()
        self.transitions: List[StateTransition] = []
        self.current_state: Optional[str] = None
        self.state_history: List[str] = []
        self.transition_callbacks: Dict[str, List[Callable]] = {}

    def add_state(self, state: str):
        """Add a new state to the machine"""
        self.states.add(state)
        if self.current_state is None:
            self.current_state = state

    def add_transition(
        self,
        from_state: str,
        to_state: str,
        probability: float,
        conditions: Optional[Dict[str, Any]] = None,
    ):
        """
        Add a probabilistic transition between states

        Args:
            from_state: Starting state
            to_state: Target state
            probability: Transition probability (0-1)
            conditions: Optional conditions for the transition
        """
        self.states.update([from_state, to_state])
        transition = StateTransition(from_state, to_state, probability, conditions)
        self.transitions.append(transition)

        logger.info(f"Added transition: {from_state} -> {to_state} (p={probability})")

    def set_initial_state(self, state: str):
        """Set the initial state of the machine"""
        if state in self.states:
            self.current_state = state
            self.state_history = [state]
        else:
            raise QuantumStateError(f"Unknown state: {state}")

    def next_state(self, quantum_state: Optional[QuantumState] = None) -> str:
        """
        Probabilistically transition to the next state

        Args:
            quantum_state: Optional QuantumState for conditional transitions

        Returns:
            New current state
        """
        if self.current_state is None:
            raise QuantumStateError("No current state set")

        # Get possible transitions
        possible_transitions = [
            t
            for t in self.transitions
            if t.from_state == self.current_state
            and self._check_conditions(t, quantum_state)
        ]

        if not possible_transitions:
            return self.current_state

        # Calculate probabilities and normalize
        probs = np.array([t.probability for t in possible_transitions])
        probs = probs / np.sum(probs)

        # Select next transition probabilistically
        next_transition = np.random.choice(possible_transitions, p=probs)
        old_state = self.current_state
        self.current_state = next_transition.to_state
        self.state_history.append(self.current_state)

        # Trigger callbacks
        self._trigger_callbacks(old_state, self.current_state)

        logger.info(f"State transition: {old_state} -> {self.current_state}")
        return self.current_state

    def _check_conditions(
        self, transition: StateTransition, quantum_state: Optional[QuantumState]
    ) -> bool:
        """Check if transition conditions are met"""
        if transition.conditions is None:
            return True

        if quantum_state is None:
            return False

        # Check all conditions
        for key, expected_value in transition.conditions.items():
            current_value = quantum_state.measure(key)
            if current_value != expected_value:
                return False

        return True

    def add_transition_callback(self, from_state: str, callback: Callable):
        """Add a callback for specific state transitions"""
        if from_state not in self.transition_callbacks:
            self.transition_callbacks[from_state] = []
        self.transition_callbacks[from_state].append(callback)

    def _trigger_callbacks(self, from_state: str, to_state: str):
        """Trigger callbacks for state transitions"""
        callbacks = self.transition_callbacks.get(from_state, [])
        for callback in callbacks:
            try:
                callback(from_state, to_state)
            except Exception as e:
                logger.error(f"Transition callback failed: {e}")

    def get_transition_probability(self, from_state: str, to_state: str) -> float:
        """Get the transition probability between two states"""
        transitions = [
            t
            for t in self.transitions
            if t.from_state == from_state and t.to_state == to_state
        ]
        return sum(t.probability for t in transitions)

    def rollback(self, steps: int = 1):
        """Rollback state history by specified number of steps"""
        if len(self.state_history) > steps:
            self.state_history = self.state_history[:-steps]
            self.current_state = self.state_history[-1]
            logger.info(f"Rolled back {steps} steps to state: {self.current_state}")
        else:
            raise QuantumStateError("Cannot rollback beyond initial state")

    def reset(self):
        """Reset to initial state"""
        if self.state_history:
            initial_state = self.state_history[0]
            self.current_state = initial_state
            self.state_history = [initial_state]
            logger.info(f"Reset to initial state: {initial_state}")

    def get_state_graph(self) -> Dict[str, List[tuple]]:
        """Get the state transition graph"""
        graph = {}
        for state in self.states:
            graph[state] = [
                (t.to_state, t.probability)
                for t in self.transitions
                if t.from_state == state
            ]
        return graph
