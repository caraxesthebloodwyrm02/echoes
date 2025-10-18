"""
Demo: Text Editor with Glimpse
Demonstrates realtime trajectory visualization for text writing
"""

import time
from pathlib import Path
from realtime_preview import create_glimpse


def simulate_writing_session():
    """Simulate a writing session with Glimpse"""
    
    print("=" * 70)
    print("TEXT EDITOR DEMO - Glimpse")
    print("=" * 70)
    print()
    
    # Create preview system
    system = create_glimpse(
        mode="timeline",
        enable_security=True,
        base_path=Path(__file__).parent
    )
    
    # Start system
    if not system.start():
        print("Failed to start system")
        return
    
    print("✓ System started with security enabled\n")
    
    # Simulate writing a story
    story_fragments = [
        "Once upon a time, ",
        "in a land far away, ",
        "there lived a young coder ",
        "who dreamed of building ",
        "a system that could predict ",
        "the future of creative work. ",
        "\n\nEvery day, ",
        "the coder worked tirelessly, ",
        "crafting algorithms ",
        "and visualizations. "
    ]
    
    print("Simulating story writing...\n")
    
    position = 0
    for i, fragment in enumerate(story_fragments):
        print(f"\n--- Fragment {i+1} ---")
        print(f"Adding: '{fragment}'")
        
        # Process input
        result = system.process_input(
            action="insert",
            position=position,
            text=fragment
        )
        
        if result.get("success"):
            # Show trajectory
            traj = result.get("trajectory", {})
            print(f"Direction: {traj.get('current_direction', 'unknown')}")
            print(f"Confidence: {traj.get('confidence', 0):.2f}")
            
            # Show suggestions if available
            suggestions = result.get("suggestions", [])
            if suggestions:
                print(f"Suggestions: {', '.join(suggestions)}")
            
            # Show predictions
            predictions = result.get("predictions", [])
            if predictions:
                print("Predictions:")
                for pred in predictions[:2]:
                    print(f"  - {pred.get('direction')}: {pred.get('probability', 0):.2f}")
        
        position += len(fragment)
        time.sleep(0.3)  # Simulate typing delay
    
    # Show ASCII preview
    print("\n" + "=" * 70)
    print("VISUAL PREVIEW (ASCII)")
    print("=" * 70)
    preview = system.get_current_preview()
    if preview:
        print(preview)
    
    # Show final state
    print("\n" + "=" * 70)
    print("FINAL STATE")
    print("=" * 70)
    state = system.get_full_state()
    print(f"Total events: {state['system']['total_events']}")
    print(f"Uptime: {state['system']['uptime']:.2f}s")
    print(f"Trajectory health: {state['trajectory']['trajectory_health']:.2f}")
    print(f"Total segments: {state['trajectory']['total_segments']}")
    
    # Export session
    output_dir = Path(__file__).parent / "exports" / "text_demo"
    system.export_session(str(output_dir))
    print(f"\n✓ Session exported to: {output_dir}")
    
    # Stop system
    system.stop()
    print("\n✓ Demo complete!")


def simulate_editing_session():
    """Simulate an editing session with deletions and replacements"""
    
    print("\n\n" + "=" * 70)
    print("TEXT EDITING DEMO - With Deletions & Replacements")
    print("=" * 70)
    print()
    
    system = create_preview_system(mode="flow", enable_security=True)
    system.start()
    
    # Initial text
    print("Writing initial draft...")
    system.process_input(action="insert", position=0, text="The quick brown fox jumps over the lazy dog")
    
    time.sleep(0.5)
    
    # Replace 'quick' with 'swift'
    print("\nReplacing 'quick' with 'swift'...")
    system.process_input(action="replace", start=4, end=9, text="swift")
    
    time.sleep(0.5)
    
    # Delete 'lazy'
    print("Deleting 'lazy'...")
    system.process_input(action="delete", start=36, end=41)
    
    time.sleep(0.5)
    
    # Add more text
    print("Adding ending...")
    current_len = len(system.input_adapter.current_content)
    system.process_input(action="insert", position=current_len, text=" in the moonlight.")
    
    # Show final result
    print("\n" + "=" * 70)
    print("FINAL TEXT")
    print("=" * 70)
    print(system.input_adapter.current_content)
    
    # Show trajectory
    print("\n" + "=" * 70)
    print("TRAJECTORY SUMMARY")
    print("=" * 70)
    summary = system.trajectory.get_trajectory_summary()
    print(f"Total points: {summary['total_points']}")
    print(f"Current direction: {summary['current_direction']}")
    print(f"Health score: {summary['trajectory_health']:.2f}")
    
    system.stop()
    print("\n✓ Editing demo complete!")


if __name__ == "__main__":
    # Run writing demo
    simulate_writing_session()
    
    # Run editing demo
    time.sleep(1)
    simulate_editing_session()
