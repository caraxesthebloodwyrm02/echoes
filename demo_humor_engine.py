#!/usr/bin/env python3
"""
Demo script showcasing the Sense of Humor Engine for pressure management
Demonstrates contextual humor, stress reduction, and pressure-aware responses
"""

import os
import sys
import time
from datetime import datetime

# Load environment variables
os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))

try:
    from core_modules.humor_engine import humor_engine, PressureLevel, HumorType
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the Echoes project root")
    sys.exit(1)


def demo_pressure_levels():
    """Demonstrate humor at different pressure levels"""
    print("\n" + "=" * 70)
    print("😄 PRESSURE-AWARE HUMOR DEMO")
    print("=" * 70)

    print("\n📊 Testing humor responses at different pressure levels:")

    contexts = [
        ("error_occurred", "When an error happens"),
        ("task_completed", "When a task is completed successfully"),
        ("high_load", "During high system load"),
        ("help", "When user needs help"),
        ("general", "General conversation"),
    ]

    for level in [
        PressureLevel.LOW,
        PressureLevel.MEDIUM,
        PressureLevel.HIGH,
        PressureLevel.CRITICAL,
        PressureLevel.OVERWHELMED,
    ]:
        print(f"\n🎯 **{level.value.upper()}** Pressure Level:")

        for context, description in contexts:
            humor_response = humor_engine.generate_humor_response(level, context)

            if humor_response:
                print(f"  {description}:")
                print(f"    📝 {humor_response.text}")
                print(f"    🎭 Type: {humor_response.humor_type.value}")
                print(f"    🎨 Style: {humor_response.delivery_style}")
                print(f"    📊 Appropriateness: {humor_response.appropriateness:.1%}")
                print()
            else:
                print(f"  {description}: No humor generated")

        print("  " + "-" * 50)


def demo_humor_types():
    """Demonstrate different types of humor"""
    print("\n" + "=" * 70)
    print("🎭 HUMOR TYPE VARIETY DEMO")
    print("=" * 70)

    humor_descriptions = {
        HumorType.WITTY: "Clever wordplay and intelligent humor",
        HumorType.SELF_DEPRECATING: "Light self-aware humor about AI limitations",
        HumorType.TECH: "Programming and technology-specific jokes",
        HumorType.ENCOURAGING: "Uplifting humor with positive reinforcement",
        HumorType.PRESSURE_RELIEF: "Stress-reducing humor for high-pressure situations",
        HumorType.CELEBRATORY: "Success celebration humor",
    }

    print("\n🎭 Exploring different humor types:")

    for humor_type, description in humor_descriptions.items():
        print(f"\n**{humor_type.value.title()}** - {description}:")

        # Test at medium pressure
        response = humor_engine.generate_humor_response(
            PressureLevel.MEDIUM, "", humor_type
        )

        if response:
            print(f"  💬 {response.text}")
            print(f"  🎨 Delivery: {response.delivery_style}")
            print(f"  📊 Appropriateness: {response.appropriateness:.1%}")
        else:
            print("  No humor available for this type")


def demo_contextual_humor():
    """Demonstrate context-aware humor generation"""
    print("\n" + "=" * 70)
    print("🧠 CONTEXTUAL HUMOR DEMO")
    print("=" * 70)

    scenarios = [
        ("error_occurred", "User encounters an error"),
        ("task_completed", "Task completed successfully"),
        ("long_processing", "Long processing time"),
        ("user_confused", "User seems confused"),
        ("high_load", "System under high load"),
    ]

    print("\n🎯 Context-aware humor responses:")

    for context, description in scenarios:
        print(f"\n**Scenario:** {description}")

        # Test at different pressure levels
        for level in [PressureLevel.LOW, PressureLevel.HIGH, PressureLevel.CRITICAL]:
            response = humor_engine.generate_humor_response(level, context)

            if response:
                print(f"  {level.value.title()}: {response.text}")
            else:
                print(f"  {level.value.title()}: No contextual humor")


def demo_pressure_tracking():
    """Demonstrate pressure tracking and metrics"""
    print("\n" + "=" * 70)
    print("📊 PRESSURE TRACKING DEMO")
    print("=" * 70)

    print("\n🔄 Simulating different load scenarios:")

    scenarios = [
        (1, False, 0.5, "Light load"),
        (3, False, 1.2, "Medium load"),
        (7, False, 3.5, "High load"),
        (15, True, 8.2, "Critical load with error"),
        (25, True, 15.0, "Overwhelmed with errors"),
    ]

    for requests, error, response_time, description in scenarios:
        print(f"\n**Scenario:** {description}")

        # Update pressure metrics
        level = humor_engine.update_pressure_metrics(requests, error, response_time)

        # Get summary
        summary = humor_engine.get_pressure_summary()

        print(f"  📈 Requests/Minute: {summary['current_rpm']}")
        print(f"  ❌ Error Count: {summary['current_errors']}")
        print(f"  🎯 Pressure Level: {summary['current_level'].title()}")
        print(f"  📊 Trend: {summary['trend'].title()}")

        # Check if humor would be used
        would_use_humor = humor_engine.should_use_humor(
            level, "high_load" if requests > 5 else ""
        )
        print(f"  😄 Humor Appropriate: {'Yes' if would_use_humor else 'No'}")

        if would_use_humor:
            humor_response = humor_engine.generate_humor_response(level, "high_load")
            if humor_response:
                print(f"  💬 Sample: {humor_response.text}")


def demo_delivery_styles():
    """Demonstrate different humor delivery styles"""
    print("\n" + "=" * 70)
    print("🎨 DELIVERY STYLES DEMO")
    print("=" * 70)

    styles = {
        "playful": "Fun and energetic delivery",
        "gentle": "Soft and comforting delivery",
        "enthusiastic": "High energy and exciting delivery",
        "deadpan": "Dry and understated delivery",
    }

    print("\n🎨 Different delivery styles:")

    for style, description in styles.items():
        print(f"\n**{style.title()}** - {description}:")

        # Generate humor and manually set style for demo
        response = humor_engine.generate_humor_response(PressureLevel.MEDIUM, "")

        if response:
            # Format based on style
            if style == "playful":
                formatted = f"😄 **{response.text}**"
            elif style == "gentle":
                formatted = f"💙 *{response.text}*"
            elif style == "enthusiastic":
                formatted = f"🎉 **{response.text}** 🎉"
            else:  # deadpan
                formatted = f"😐 {response.text}"

            print(f"  {formatted}")


def demo_humor_integration():
    """Demonstrate how humor integrates with responses"""
    print("\n" + "=" * 70)
    print("🔗 HUMOR INTEGRATION DEMO")
    print("=" * 70)

    print("\n💬 Simulated assistant responses with humor:")

    scenarios = [
        {
            "pressure": PressureLevel.LOW,
            "context": "task_completed",
            "base_response": "I've successfully completed the data analysis task.",
            "description": "Normal task completion",
        },
        {
            "pressure": PressureLevel.HIGH,
            "context": "high_load",
            "base_response": "I'm processing multiple complex requests simultaneously.",
            "description": "High pressure situation",
        },
        {
            "pressure": PressureLevel.CRITICAL,
            "context": "error_occurred",
            "base_response": "There was an error processing your request.",
            "description": "Error during critical load",
        },
        {
            "pressure": PressureLevel.OVERWHELMED,
            "context": "high_load",
            "base_response": "System is at maximum capacity.",
            "description": "Overwhelmed system",
        },
    ]

    for scenario in scenarios:
        print(f"\n**{scenario['description']}:**")
        print(f"  Base: {scenario['base_response']}")

        # Check if humor would be added
        would_use_humor = humor_engine.should_use_humor(
            scenario["pressure"], scenario["context"]
        )

        if would_use_humor:
            humor_response = humor_engine.generate_humor_response(
                scenario["pressure"], scenario["context"]
            )
            if humor_response:
                # Format the humor
                if humor_response.delivery_style == "playful":
                    humor_text = f"\n\n😄 **{humor_response.text}**"
                elif humor_response.delivery_style == "gentle":
                    humor_text = f"\n\n💙 *{humor_response.text}*"
                elif humor_response.delivery_style == "enthusiastic":
                    humor_text = f"\n\n🎉 **{humor_response.text}**"
                else:
                    humor_text = f"\n\n😊 {humor_response.text}"

                print(f"  With humor: {scenario['base_response']}{humor_text}")
        else:
            print(f"  With humor: {scenario['base_response']} (no humor added)")


def demo_pressure_management():
    """Demonstrate pressure management features"""
    print("\n" + "=" * 70)
    print("🛡️ PRESSURE MANAGEMENT DEMO")
    print("=" * 70)

    print("\n🔄 Simulating pressure buildup and relief:")

    # Simulate increasing pressure
    print("\n📈 Building up pressure...")

    for i in range(5):
        # Simulate increasing load
        requests = 2 + i * 5
        error = i > 3
        response_time = 0.5 + i * 2

        level = humor_engine.update_pressure_metrics(requests, error, response_time)
        summary = humor_engine.get_pressure_summary()

        print(
            f"  Step {i+1}: {summary['current_level'].title()} pressure "
            f"({summary['current_rpm']} RPM, {summary['current_errors']} errors)"
        )

        # Show humor probability
        would_use_humor = humor_engine.should_use_humor(
            level, "high_load" if i > 1 else ""
        )
        print(f"           Humor probability: {'High' if would_use_humor else 'Low'}")

    # Show recommendations
    print(f"\n💡 Current pressure recommendations:")
    current_level = PressureLevel(humor_engine.get_pressure_summary()["current_level"])

    recommendations = {
        PressureLevel.LOW: "Perfect time for complex tasks! 🎯",
        PressureLevel.MEDIUM: "Good performance, monitoring active 📊",
        PressureLevel.HIGH: "Consider breaking down complex tasks 🔧",
        PressureLevel.CRITICAL: "High load detected - humor engaged for stress relief 😄",
        PressureLevel.OVERWHELMED: "Maximum load - taking measures to reduce pressure 🛡️",
    }

    print(f"  {recommendations.get(current_level, 'Monitoring situation...')}")

    # Reset for next demo
    humor_engine.reset_metrics()


def demo_interactive_features():
    """Demonstrate interactive humor features"""
    print("\n" + "=" * 70)
    print("🎮 INTERACTIVE HUMOR FEATURES DEMO")
    print("=" * 70)

    print("\n🎮 Testing interactive humor commands:")

    # Test joke generation for different levels
    levels = ["low", "medium", "high", "critical", "overwhelmed"]

    for level in levels:
        print(f"\n**Joke for {level} pressure:**")

        pressure_enum = PressureLevel(level)
        joke_response = humor_engine.generate_humor_response(
            pressure_enum, "user_requested"
        )

        if joke_response:
            print(f"  {joke_response.text}")
            print(f"  Type: {joke_response.humor_type.value}")
            print(f"  Style: {joke_response.delivery_style}")
        else:
            print("  No joke available for this level")


def main():
    """Run all humor demos"""
    print("\n✨ Welcome to the Sense of Humor Engine Demo!")
    print(
        "This showcases pressure-aware humor for stress management and user engagement."
    )

    # Run all demos
    demo_pressure_levels()
    demo_humor_types()
    demo_contextual_humor()
    demo_pressure_tracking()
    demo_delivery_styles()
    demo_humor_integration()
    demo_pressure_management()
    demo_interactive_features()

    print("\n" + "=" * 70)
    print("🎉 Humor Engine Demo Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Pressure-aware humor generation (5 levels)")
    print("  ✅ 6 different humor types for various contexts")
    print("  ✅ Contextual humor based on situation")
    print("  ✅ Real-time pressure tracking and metrics")
    print("  ✅ Multiple delivery styles (playful, gentle, enthusiastic, deadpan)")
    print("  ✅ Intelligent integration with assistant responses")
    print("  ✅ Pressure management and stress reduction")
    print("  ✅ Interactive humor commands")

    print("\nPressure Level Progression:")
    print("  Low → Medium → High → Critical → Overwhelmed")
    print("  Humor probability increases with pressure!")

    print("\nTry the interactive mode with:")
    print("  python assistant_v2_core.py")
    print("  Then try commands like:")
    print("    humor                  - Show humor status and pressure")
    print("    pressure               - Detailed pressure analysis")
    print("    joke [level]           - Tell a joke for specific pressure")
    print("    joke high              - High-pressure joke")
    print("    joke critical          - Critical-pressure joke")


if __name__ == "__main__":
    main()
