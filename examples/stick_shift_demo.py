"""
Stick Shift Controller Demo

Demonstrates the adaptive "stick shift" behavior control system
inspired by Ableton grid quantization and manual transmission.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from app.core.stick_shift_controller import (
    Gear,
    StickShiftController,
    calculate_task_complexity,
    create_stick_shift,
)

load_dotenv()


def demo_basic_shifting():
    """Demo 1: Basic gear shifting."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Gear Shifting")
    print("=" * 70 + "\n")

    controller = create_stick_shift(Gear.THIRD)

    print("Starting in THIRD gear (balanced)")
    print(controller.get_status())

    input("\n▶ Press Enter to DOWNSHIFT...")
    controller.downshift()

    input("\n▶ Press Enter to DOWNSHIFT again...")
    controller.downshift()

    input("\n▶ Press Enter to UPSHIFT...")
    controller.upshift()

    input("\n▶ Press Enter to UPSHIFT to FIFTH...")
    controller.upshift()
    controller.upshift()


def demo_processing_config():
    """Demo 2: Show processing configuration for each gear."""
    print("\n" + "=" * 70)
    print("DEMO 2: Processing Configuration by Gear")
    print("=" * 70 + "\n")

    controller = StickShiftController()

    for gear in Gear:
        controller.shift_to(gear, manual=True)
        config = controller.get_processing_config()

        print(f"\n{gear.name} GEAR:")
        print(f"  Grid: {config['grid_resolution']}")
        print(f"  Time Signature: {config['time_signature']}")
        print(f"  Quantization: {config['quantization']*100:.0f}%")
        print(f"  Inference Depth: {config['inference_depth']}")
        print(f"  RPM: {config['rpm']}")
        print(f"  Style: {config['style']}")
        print(f"  Temperature: {config['temperature']:.2f}")
        print(f"  Top-P: {config['top_p']:.2f}")
        print(f"  Max Tokens: {config['max_tokens']}")

        input(f"\n▶ Press Enter to see {gear.name} gear...")


def demo_auto_shift():
    """Demo 3: Automatic shifting based on task complexity."""
    print("\n" + "=" * 70)
    print("DEMO 3: Automatic Gear Selection")
    print("=" * 70 + "\n")

    controller = StickShiftController()

    tasks = [
        ("Simple cleanup task", 0.1),
        ("Organize small project", 0.3),
        ("Refactor module", 0.5),
        ("Redesign architecture", 0.7),
        ("Complete system overhaul", 0.95),
    ]

    for task_desc, complexity in tasks:
        print(f"\nTask: {task_desc}")
        print(f"Complexity: {complexity:.2f}")

        controller.auto_shift(complexity)
        config = controller.get_processing_config()

        print(f"Selected: {config['gear']} gear")
        print(f"  Grid: {config['grid_resolution']}")
        print(f"  RPM: {config['rpm']}")
        print(f"  Style: {config['style']}")

        input("▶ Press Enter for next task...")


def demo_boost_and_cruise():
    """Demo 4: Boost and cruise modes."""
    print("\n" + "=" * 70)
    print("DEMO 4: Boost and Cruise Modes")
    print("=" * 70 + "\n")

    controller = StickShiftController(Gear.THIRD)

    print("Starting in THIRD gear")
    print(controller.get_status())

    input("\n▶ Press Enter to activate BOOST MODE...")
    boost_config = controller.boost_mode()
    print(f"\nBoosted RPM: {boost_config['rpm']}")
    print(f"Inference Depth: {boost_config['inference_depth']}")
    print(f"Temperature: {boost_config['temperature']:.2f}")

    input("\n▶ Press Enter to activate CRUISE MODE...")
    cruise_config = controller.cruise_mode()
    print(f"\nCruise RPM: {cruise_config['rpm']}")
    print(f"Grid: {cruise_config['grid_resolution']}")
    print(f"Style: {cruise_config['style']}")


def demo_task_complexity_calculation():
    """Demo 5: Task complexity calculation."""
    print("\n" + "=" * 70)
    print("DEMO 5: Task Complexity Calculation")
    print("=" * 70 + "\n")

    tasks = [
        "Use assistant to organize the codebase",
        "Use assistant to refactor complex module",
        "Use assistant to completely redesign architecture",
        "Use assistant to fix simple typo",
        "Use assistant to optimize performance across entire system",
    ]

    controller = StickShiftController()

    for task in tasks:
        # Calculate complexity
        complexity = calculate_task_complexity(task, context_size=50)

        print(f"\nTask: {task}")
        print(f"Calculated Complexity: {complexity:.2f}")

        # Auto shift
        controller.auto_shift(complexity)

        print(f"Selected Gear: {controller.current_gear.name}")

        input("▶ Press Enter for next task...")


def demo_quantization_swing():
    """Demo 6: Show quantization swing effect."""
    print("\n" + "=" * 70)
    print("DEMO 6: Quantization Swing Effect")
    print("=" * 70 + "\n")

    print("Demonstrating how quantization creates 'swing' in behavior...\n")

    controller = StickShiftController(Gear.SECOND)
    profile = controller.get_current_profile()

    print(f"Gear: {profile.gear.name}")
    print(f"Base Quantization: {profile.quantization*100:.0f}%")
    print("\nGenerating 10 behavior modifiers with swing:\n")

    for i in range(10):
        modifier = profile.get_behavior_modifier()
        deviation = (modifier - 1.0) * 100

        bar = "=" * int(abs(deviation) * 5)
        direction = "+" if deviation > 0 else "-"

        print(f"  {i+1:2d}. {modifier:.3f} ({direction}{abs(deviation):5.2f}%) {bar}")

    print("\nThis 'swing' creates versatile, non-robotic behavior!")


def demo_interactive():
    """Demo 7: Interactive stick shift control."""
    print("\n" + "=" * 70)
    print("DEMO 7: Interactive Control")
    print("=" * 70 + "\n")

    controller = StickShiftController(Gear.THIRD)

    print("Interactive Stick Shift Controller")
    print("\nCommands:")
    print("  d - Downshift")
    print("  u - Upshift")
    print("  1-5 - Shift to specific gear")
    print("  b - Boost mode")
    print("  c - Cruise mode")
    print("  s - Show status")
    print("  q - Quit")

    while True:
        print("\n" + controller.get_status())

        cmd = input("\nCommand: ").strip().lower()

        if cmd == "q":
            print("\nExiting...")
            break
        elif cmd == "d":
            controller.downshift()
        elif cmd == "u":
            controller.upshift()
        elif cmd in ["1", "2", "3", "4", "5"]:
            gear = Gear(int(cmd))
            controller.shift_to(gear)
        elif cmd == "b":
            controller.boost_mode()
        elif cmd == "c":
            controller.cruise_mode()
        elif cmd == "s":
            config = controller.get_processing_config()
            print("\nCurrent Configuration:")
            for key, value in config.items():
                print(f"  {key}: {value}")
        else:
            print("Invalid command")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("🏎️  STICK SHIFT CONTROLLER DEMO 🏎️")
    print("=" * 70)
    print("\nAdaptive AI Behavior Control")
    print("Inspired by Ableton grid quantization & manual transmission")
    print("=" * 70)

    try:
        demo_basic_shifting()

        input("\n\n▶ Press Enter to continue to Demo 2...")
        demo_processing_config()

        input("\n\n▶ Press Enter to continue to Demo 3...")
        demo_auto_shift()

        input("\n\n▶ Press Enter to continue to Demo 4...")
        demo_boost_and_cruise()

        input("\n\n▶ Press Enter to continue to Demo 5...")
        demo_task_complexity_calculation()

        input("\n\n▶ Press Enter to continue to Demo 6...")
        demo_quantization_swing()

        input("\n\n▶ Press Enter to continue to Demo 7 (Interactive)...")
        demo_interactive()

        print("\n" + "=" * 70)
        print("✅ All demos completed!")
        print("=" * 70 + "\n")

        print("💡 Integration with Lumina:")
        print(
            """
The Stick Shift Controller is now integrated into the autonomous executor.
It automatically:
- Calculates task complexity
- Selects appropriate gear
- Adjusts AI behavior (temperature, depth, tokens)
- Applies grid quantization for "swing"
- Shifts gears during execution (boost/cruise)

This creates versatile, adaptive AI behavior without extensive tuning!
        """
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted.\n")


if __name__ == "__main__":
    main()
