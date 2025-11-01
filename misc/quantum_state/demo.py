#!/usr/bin/env python3
"""
Quantum State Management Demo
=============================

Demonstration of the quantum-inspired state management system.
Shows how to use superposition, entanglement, and probabilistic transitions.
"""

import sys
import os
import time
from datetime import datetime

# Add the Echoes project directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from quantum_state.quantum_state_manager import QuantumStateManager

def demo_basic_operations():
    """Demonstrate basic quantum state operations"""
    print("=== Basic Quantum State Operations ===\n")

    qsm = QuantumStateManager()
    qsm.initialize_quantum_states()

    # Update states with entanglement
    print("1. Updating states with entanglement:")
    qsm.update_state('user_session', 'active', entangle_with=['permissions', 'features'])
    qsm.update_state('permissions', 'admin')

    print(f"   User session: {qsm.measure_state('user_session')}")
    print(f"   Permissions: {qsm.measure_state('permissions')}")
    print(f"   Entangled states: {qsm.get_entangled_states('user_session')}")

    # Demonstrate superposition
    print("\n2. Measuring superposition:")
    superposition = qsm.get_superposition(['system_status', 'processing', 'authentication'])
    for key, value in superposition.items():
        print(f"   {key}: {value}")

    # Show state transitions
    print("\n3. Probabilistic state transitions:")
    for i in range(5):
        current = qsm.transition_state()
        print(f"   Transition {i+1}: {current}")
        time.sleep(0.1)  # Small delay for demonstration

def demo_observer_pattern():
    """Demonstrate the observer pattern for state changes"""
    print("\n=== Observer Pattern Demo ===\n")

    def state_change_logger(key, old_val, new_val):
        timestamp = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] State changed: {key} | {old_val} -> {new_val}")

    def alert_on_error(key, old_val, new_val):
        if key == 'error_state' and new_val is not None:
            print(f"🚨 ALERT: Error detected! {new_val}")

    qsm = QuantumStateManager()
    qsm.initialize_quantum_states()

    # Add observers
    qsm.add_observer(state_change_logger)
    qsm.add_observer(alert_on_error)

    print("Observers added. Making state changes...")

    # Trigger state changes that will notify observers
    qsm.update_state('processing', 'active')
    qsm.update_state('error_state', 'Connection timeout')
    qsm.update_state('processing', 'completed')
    qsm.update_state('error_state', None)

def demo_interference():
    """Demonstrate quantum interference patterns"""
    print("\n=== Quantum Interference Demo ===\n")

    qsm = QuantumStateManager()
    qsm.initialize_quantum_states()

    # Add interference between processing states
    print("Adding interference between 'processing' and 'success' states...")
    qsm.simulate_interference('processing', 'success', 0.3)

    # Observe transitions with interference
    print("State transitions with interference:")
    for i in range(10):
        current = qsm.transition_state()
        print(f"   Step {i+1}: {current}")

def demo_persistence():
    """Demonstrate state persistence and recovery"""
    print("\n=== Persistence Demo ===\n")

    persistence_file = "quantum_state_demo.json"

    # Create and configure state manager
    qsm1 = QuantumStateManager(persistence_file)
    qsm1.initialize_quantum_states()

    # Make some changes
    qsm1.update_state('custom_metric', 'test_value')
    qsm1.update_state('processing', 'demo_active')

    print("Saving state...")
    qsm1.save_state()

    # Create new instance and load state
    qsm2 = QuantumStateManager(persistence_file)
    qsm2.load_state()

    print("Loaded state from file:")
    print(f"   Custom metric: {qsm2.measure_state('custom_metric')}")
    print(f"   Processing: {qsm2.measure_state('processing')}")
    print(f"   Current machine state: {qsm2.state_machine.current_state}")

    # Clean up
    if os.path.exists(persistence_file):
        os.remove(persistence_file)

def demo_performance():
    """Demonstrate performance monitoring"""
    print("\n=== Performance Monitoring Demo ===\n")

    qsm = QuantumStateManager()
    qsm.initialize_quantum_states()

    # Perform multiple operations
    print("Performing 100 state updates...")
    for i in range(100):
        qsm.update_state(f'test_state_{i}', f'value_{i}')
        if i % 20 == 0:
            qsm.transition_state()

    # Show metrics
    metrics = qsm.get_metrics()
    print("Performance metrics:")
    print(f"   Total updates: {metrics.total_updates}")
    print(f"   Total measurements: {metrics.total_measurements}")
    print(f"   Average transition time: {metrics.average_transition_time:.6f}s")
    print(f"   Entangled states: {metrics.entangled_states_count}")

def main():
    """Run all demonstrations"""
    print("🌟 Quantum-Inspired State Management System Demo 🌟\n")
    print("=" * 60)

    try:
        demo_basic_operations()
        demo_observer_pattern()
        demo_interference()
        demo_persistence()
        demo_performance()

        print("\n" + "=" * 60)
        print("✅ All demonstrations completed successfully!")
        print("\nQuantum concepts implemented:")
        print("  • Superposition: Multiple state configurations")
        print("  • Entanglement: Correlated state updates")
        print("  • Measurement: State value retrieval")
        print("  • Probabilistic Transitions: Uncertainty modeling")
        print("  • Interference: Complex state interactions")
        print("  • Observer Pattern: Reactive state management")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
