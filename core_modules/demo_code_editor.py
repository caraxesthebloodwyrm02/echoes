"""
Demo: Code Editor with Glimpse
Demonstrates realtime trajectory visualization for coding
"""

import time
from pathlib import Path
from realtime_preview import create_glimpse


def simulate_coding_session():
    """Simulate a coding session with Glimpse"""

    print("=" * 70)
    print("CODE EDITOR DEMO - Glimpse")
    print("=" * 70)
    print()

    # Create preview system with tree visualization
    system = create_glimpse(mode="tree", enable_security=True, base_path=Path(__file__).parent)

    # Register custom direction analyzer for code
    def code_analyzer(points):
        """Analyze code direction based on patterns"""
        from core_trajectory import TrajectoryDirection

        if not points:
            return TrajectoryDirection.UNCERTAIN

        recent_content = points[-1].content

        # Expanding: adding new functions, classes
        if "def " in recent_content or "class " in recent_content:
            return TrajectoryDirection.EXPANDING

        # Converging: refining existing code
        if recent_content.count("#") > 2:  # Adding comments
            return TrajectoryDirection.CONVERGING

        # Pivoting: imports or major changes
        if "import " in recent_content:
            return TrajectoryDirection.PIVOTING

        return TrajectoryDirection.STABLE

    system.trajectory.register_analyzer(code_analyzer)

    # Start system
    if not system.start():
        print("Failed to start system")
        return

    print("✓ System started with code-aware analyzer\n")

    # Simulate writing a Python function
    code_fragments = [
        "import math\n",
        "import time\n\n",
        "def calculate_trajectory(points):\n",
        '    """\n',
        "    Calculate trajectory metrics\n",
        '    """\n',
        "    if not points:\n",
        "        return None\n\n",
        "    # Compute distance\n",
        "    total_distance = 0\n",
        "    for i in range(1, len(points)):\n",
        "        dx = points[i]['x'] - points[i-1]['x']\n",
        "        dy = points[i]['y'] - points[i-1]['y']\n",
        "        total_distance += math.sqrt(dx**2 + dy**2)\n\n",
        "    return total_distance\n",
    ]

    print("Simulating code writing...\n")

    position = 0
    for i, fragment in enumerate(code_fragments):
        print(f"\n--- Code Fragment {i+1} ---")
        preview_text = fragment.replace("\n", "\\n")
        if len(preview_text) > 50:
            preview_text = preview_text[:50] + "..."
        print(f"Adding: {preview_text}")

        # Process input
        result = system.process_input(action="insert", position=position, text=fragment)

        if result.get("success"):
            # Show trajectory
            traj = result.get("trajectory", {})
            print(f"Direction: {traj.get('current_direction', 'unknown')}")
            print(f"Confidence: {traj.get('confidence', 0):.2f}")

            # Show cause-effect chain
            chain = traj.get("cause_effect_chain", [])
            if chain:
                print(f"Cause-effect: {' '.join(chain[-2:])}")

            # Show predictions
            predictions = result.get("predictions", [])
            if predictions and i % 3 == 0:  # Show occasionally
                print("Next step predictions:")
                for pred in predictions[:2]:
                    print(f"  - {pred.get('description')} ({pred.get('probability', 0):.1%})")

        position += len(fragment)
        time.sleep(0.4)  # Simulate typing delay

    # Show final code
    print("\n" + "=" * 70)
    print("FINAL CODE")
    print("=" * 70)
    print(system.input_adapter.current_content)

    # Show coding metrics
    print("\n" + "=" * 70)
    print("CODING METRICS")
    print("=" * 70)
    state = system.get_full_state()
    print(f"Total events: {state['system']['total_events']}")
    print(f"Typing velocity: {state['input']['typing_velocity']:.2f} chars/sec")
    print(f"Edit intensity: {state['input']['edit_intensity']:.2f} edits/sec")
    print(f"Trajectory segments: {state['trajectory']['total_segments']}")

    # Show security status
    if "security" in state:
        sec = state["security"]
        if sec.get("context"):
            print(f"\nSecurity shield: {sec['context']['shield_factor']:.2f}")
            print(f"Risk level: {sec['context']['risk_level']}")

    # Export session
    output_dir = Path(__file__).parent / "exports" / "code_demo"
    system.export_session(str(output_dir))
    print(f"\n✓ Session exported to: {output_dir}")

    system.stop()
    print("\n✓ Demo complete!")


def simulate_refactoring_session():
    """Simulate code refactoring with multiple edits"""

    print("\n\n" + "=" * 70)
    print("CODE REFACTORING DEMO")
    print("=" * 70)
    print()

    system = create_preview_system(mode="heatmap", enable_security=True)
    system.start()

    # Initial code
    print("Writing initial code...")
    initial_code = """def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
    system.process_input(action="insert", position=0, text=initial_code)

    time.sleep(0.5)

    # Refactor: add type hints
    print("\nRefactoring: Adding type hints...")
    system.process_input(action="replace", start=4, end=11, text="process(data: list)")

    time.sleep(0.5)

    # Add docstring
    print("Adding docstring...")
    docstring = '    """Process positive numbers by doubling them"""\n'
    system.process_input(action="insert", position=27, text=docstring)

    # Show heatmap preview (shows where edits are concentrated)
    print("\n" + "=" * 70)
    print("EDIT HEATMAP (shows editing intensity)")
    print("=" * 70)
    preview = system.get_current_preview()
    if preview:
        print(preview)

    # Show refactoring trajectory
    summary = system.trajectory.get_trajectory_summary()
    print("\n" + "=" * 70)
    print("REFACTORING TRAJECTORY")
    print("=" * 70)
    print(f"Direction: {summary['current_direction']}")
    print(f"Health: {summary['trajectory_health']:.2f}")

    system.stop()
    print("\n✓ Refactoring demo complete!")


def demonstrate_all_visualization_modes():
    """Demonstrate all visualization modes"""

    print("\n\n" + "=" * 70)
    print("VISUALIZATION MODES SHOWCASE")
    print("=" * 70)
    print()

    modes = ["timeline", "tree", "flow", "heatmap"]

    for mode in modes:
        print(f"\n--- {mode.upper()} MODE ---")

        system = create_preview_system(mode=mode, enable_security=False)
        system.start()

        # Add some sample code
        system.process_input(action="insert", position=0, text="def hello():")
        system.process_input(action="insert", position=12, text="\n    print('Hello')")
        system.process_input(action="insert", position=31, text="\n    return True")

        # Generate preview
        system._generate_preview()

        # Show ASCII preview
        preview = system.get_current_preview()
        if preview:
            print(preview)

        system.stop()
        time.sleep(0.3)

    print("\n✓ Visualization showcase complete!")


if __name__ == "__main__":
    # Run coding demo
    simulate_coding_session()

    # Run refactoring demo
    time.sleep(1)
    simulate_refactoring_session()

    # Show all visualization modes
    time.sleep(1)
    demonstrate_all_visualization_modes()
