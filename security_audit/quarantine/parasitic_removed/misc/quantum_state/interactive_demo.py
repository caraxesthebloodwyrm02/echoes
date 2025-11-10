#!/usr/bin/env python3
"""
Quantum State Management Interactive Demo
=========================================

Following the user's workflow:
1. Import QuantumState and QuantumStateManager
2. Create a state, define variables
3. Attach watchers if needed
4. Use QuantumStateMachine to apply transitions
5. Call manager.update() to process
6. Save with manager.save() and load with manager.load()
7. Run main loop to observe dynamic changes
"""

import os
import sys
import time
from datetime import datetime

# Add the Echoes project directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Step 1: Import QuantumState and QuantumStateManager
from quantum_state.quantum_state_manager import QuantumStateManager


def setup_watchers(qsm):
    """Step 3: Attach watchers if needed"""

    def state_change_watcher(key, old_val, new_val):
        """Watch for any state changes"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🔄 State changed: {key}")
        print(f"   Before: {old_val}")
        print(f"   After:  {new_val}")
        print()

    def error_alert_watcher(key, old_val, new_val):
        """Special watcher for errors"""
        if key == "error_state" and new_val is not None:
            print(f"🚨 ALERT: Error detected - {new_val}")
            print()

    def transition_watcher(from_state, to_state):
        """Watch state machine transitions"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🔀 State Machine: {from_state} → {to_state}")
        print()

    # Add observers
    qsm.add_observer(state_change_watcher)
    qsm.add_observer(error_alert_watcher)
    qsm.add_transition_callback("idle", transition_watcher)
    qsm.add_transition_callback("processing", transition_watcher)

    print("✓ Watchers attached")
    print()


def setup_state_machine_transitions(qsm):
    """Setup custom state machine transitions"""
    # Add some custom states and transitions
    qsm.state_machine.add_state("waiting")
    qsm.state_machine.add_state("running")
    qsm.state_machine.add_state("completed")
    qsm.state_machine.add_state("failed")

    # Define transitions with probabilities
    qsm.state_machine.add_transition("waiting", "running", 0.8)
    qsm.state_machine.add_transition("running", "completed", 0.7)
    qsm.state_machine.add_transition("running", "failed", 0.3)
    qsm.state_machine.add_transition("failed", "waiting", 0.6)
    qsm.state_machine.add_transition("completed", "waiting", 0.9)

    qsm.state_machine.set_initial_state("waiting")


def main():
    """Main workflow demonstration"""
    print("🌟 Quantum State Management Interactive Demo 🌟\n")
    print("=" * 60)
    print("Following the specified workflow...\n")

    try:
        # Step 2: Create a state, define variables
        print("1. Creating state and defining variables...")
        persistence_file = "interactive_demo_state.json"
        qsm = QuantumStateManager(persistence_file)

        # Initialize with basic quantum states
        qsm.initialize_quantum_states()

        # Define custom variables with entanglement
        qsm.update_state(
            "temperature", 25.0, entangle_with=["climate_control", "energy_usage"]
        )
        qsm.update_state(
            "user_activity", "idle", entangle_with=["power_mode", "notifications"]
        )
        qsm.update_state(
            "network_status", "connected", entangle_with=["data_sync", "cloud_backup"]
        )
        qsm.update_state(
            "battery_level", 85, entangle_with=["power_saving", "performance_mode"]
        )

        print("✓ State created with variables:")
        print(f"   Temperature: {qsm.measure_state('temperature')}°C")
        print(f"   User Activity: {qsm.measure_state('user_activity')}")
        print(f"   Network Status: {qsm.measure_state('network_status')}")
        print(f"   Battery Level: {qsm.measure_state('battery_level')}%")
        print()

        # Step 3: Attach watchers
        print("2. Setting up watchers...")
        setup_watchers(qsm)

        # Step 4: Use QuantumStateMachine to apply transitions
        print("3. Setting up state machine transitions...")
        setup_state_machine_transitions(qsm)
        print("✓ State machine configured")
        print()

        # Step 5: Call manager.update() to process (using update_state)
        print("4. Processing state updates...")
        qsm.update_state("temperature", 28.5)  # This will trigger entangled updates
        qsm.update_state(
            "user_activity", "active"
        )  # This will trigger entangled updates
        qsm.update_state("battery_level", 72)  # This will trigger entangled updates

        print("✓ State updates processed")
        print()

        # Step 6: Save with manager.save() and load with manager.load()
        print("5. Saving and loading state...")
        # persistence_file already defined above

        print("   Saving state...")
        qsm.save_state()

        # Create a new instance and load
        print("   Loading state in new instance...")
        qsm_loaded = QuantumStateManager(persistence_file)
        qsm_loaded.load_state()

        print("✓ State saved and loaded successfully")
        print()

        # Step 7: Run main loop to observe dynamic changes
        print("6. Running main loop to observe dynamic changes...")
        print("   (Press Ctrl+C to stop)\n")

        loop_count = 0
        max_loops = 20  # Limit for demo purposes

        while loop_count < max_loops:
            loop_count += 1
            print(f"--- Loop {loop_count}/{max_loops} ---")

            # Random state changes to simulate dynamic behavior
            import random

            # Randomly update some states
            if random.random() < 0.3:  # 30% chance
                temp_change = random.uniform(-2, 2)
                new_temp = qsm_loaded.measure_state("temperature") + temp_change
                qsm_loaded.update_state("temperature", round(new_temp, 1))

            if random.random() < 0.2:  # 20% chance
                activities = ["idle", "active", "busy", "away"]
                new_activity = random.choice(activities)
                qsm_loaded.update_state("user_activity", new_activity)

            if random.random() < 0.1:  # 10% chance
                statuses = ["connected", "disconnected", "weak", "offline"]
                new_status = random.choice(statuses)
                qsm_loaded.update_state("network_status", new_status)

            # Apply state machine transition
            current_state = qsm_loaded.transition_state()
            print(f"   Current state machine state: {current_state}")

            # Show current superposition
            if loop_count % 5 == 0:  # Every 5 loops
                print("   Current superposition:")
                superposition = qsm_loaded.get_superposition(
                    ["temperature", "user_activity", "network_status", "battery_level"]
                )
                for key, value in superposition.items():
                    print(f"     {key}: {value}")
                print()

            time.sleep(0.5)  # Brief pause between loops

        print("\n" + "=" * 60)
        print("✅ Interactive demo completed successfully!")
        print("\nWorkflow Summary:")
        print("  ✓ Imported QuantumState and QuantumStateManager")
        print("  ✓ Created state and defined variables")
        print("  ✓ Attached watchers for state changes")
        print("  ✓ Configured QuantumStateMachine with transitions")
        print("  ✓ Processed state updates")
        print("  ✓ Saved and loaded state persistence")
        print("  ✓ Ran main loop observing dynamic changes")

        # Clean up
        if os.path.exists(persistence_file):
            os.remove(persistence_file)
            print("  ✓ Cleaned up persistence file")

    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
