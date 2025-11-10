#!/usr/bin/env python3
"""
Archer Framework - Practical Usage Examples

This script demonstrates real-world applications of the Archer Framework
across different communication domains.
"""

import sys
import time
from pathlib import Path

# Add the parent directory to the path to import communication module
sys.path.append(str(Path(__file__).parent.parent))

from communication import (ArcherFramework, CommunicationMessage,
                           CommunicationType, create_communicator)


def example_1_basic_messaging():
    """Example 1: Basic messaging across different types"""
    print("🚀 Example 1: Basic Messaging")
    print("-" * 40)

    framework = ArcherFramework()

    # Register different communicators
    ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {"method": "queue"})
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL, {"style": "assertive"}
    )
    physics_comm = create_communicator(CommunicationType.PHYSICS, {"medium": "air"})

    framework.register_communicator(CommunicationType.INTERPROCESS, ipc_comm)
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)
    framework.register_communicator(CommunicationType.PHYSICS, physics_comm)

    # Send test messages
    messages = [
        CommunicationMessage(
            content="Process coordination message",
            sender="process_a",
            receiver="process_b",
            message_type=CommunicationType.INTERPROCESS,
            priority=8,
        ),
        CommunicationMessage(
            content="I appreciate your perspective on this matter",
            sender="user",
            receiver="assistant",
            message_type=CommunicationType.PSYCHOLOGICAL,
            priority=6,
        ),
        CommunicationMessage(
            content="Signal transmission data",
            sender="transmitter",
            receiver="receiver",
            message_type=CommunicationType.PHYSICS,
            priority=5,
            metadata={"frequency": 2.4e9, "power": 1.0},
        ),
    ]

    for message in messages:
        result = framework.send_message(message)
        framework.print_output(f"✅ {message.message_type.value}: {result.message}")
        if result.metadata:
            framework.print_output(f"   📊 Metadata: {result.metadata}")

    # Show metrics
    framework.print_output("\n📈 Performance Metrics:")
    metrics = framework.get_metrics()
    for key, value in metrics.items():
        framework.print_output(f"   {key}: {value:.4f}")

    print()


def example_2_psychological_communication():
    """Example 2: Psychological communication analysis"""
    print("🧠 Example 2: Psychological Communication Analysis")
    print("-" * 50)

    framework = ArcherFramework()

    # Test different communication styles
    styles = ["assertive", "passive", "aggressive"]
    test_messages = [
        "I understand your concerns and would like to propose a solution",
        "Whatever you think is best, I don't really have an opinion",
        "You're wrong and this is how we're going to do it!",
        "I feel excited about the opportunity to collaborate on this project",
        "This situation is frustrating and needs immediate attention",
    ]

    for style in styles:
        framework.print_output(f"\n🎭 Testing {style} communication style:")

        psych_comm = create_communicator(
            CommunicationType.PSYCHOLOGICAL, {"style": style, "ei_level": 0.8}
        )
        framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

        for content in test_messages:
            message = CommunicationMessage(
                content=content,
                sender="user",
                receiver="system",
                message_type=CommunicationType.PSYCHOLOGICAL,
            )

            result = framework.send_message(message)
            if result.success and result.metadata:
                tone = result.metadata.get("emotional_tone", "unknown")
                clarity = result.metadata.get("clarity_score", 0)
                empathy = result.metadata.get("empathy_score", 0)

                framework.print_output(f"   📝 '{content[:30]}...'")
                framework.print_output(
                    f"      Tone: {tone}, Clarity: {clarity:.2f}, Empathy: {empathy:.2f}"
                )

    print()


def example_3_physics_signal_simulation():
    """Example 3: Physics signal transmission simulation"""
    print("📡 Example 3: Physics Signal Transmission Simulation")
    print("-" * 55)

    framework = ArcherFramework()

    # Test different media and conditions
    test_scenarios = [
        {"medium": "air", "frequency": 2.4e9, "power": 1.0, "distance": 100},
        {"medium": "cable", "frequency": 1e6, "power": 5.0, "distance": 1000},
        {"medium": "fiber", "frequency": 1.55e9, "power": 10.0, "distance": 10000},
        {"medium": "vacuum", "frequency": 5e9, "power": 0.1, "distance": 1000},
    ]

    for scenario in test_scenarios:
        framework.print_output(f"\n🌊 Testing {scenario['medium'].upper()} medium:")

        physics_comm = create_communicator(CommunicationType.PHYSICS, scenario)
        framework.register_communicator(CommunicationType.PHYSICS, physics_comm)

        message = CommunicationMessage(
            content="Signal data packet",
            sender="transmitter",
            receiver="receiver",
            message_type=CommunicationType.PHYSICS,
            metadata=scenario,
        )

        result = framework.send_message(message)
        if result.success and result.metadata:
            strength = result.metadata.get("signal_strength", 0)
            attenuation = result.metadata.get("attenuation", 0)

            framework.print_output(f"   📊 Frequency: {scenario['frequency']:.2e} Hz")
            framework.print_output(f"   💪 Signal Strength: {strength:.3f}")
            framework.print_output(f"   📉 Attenuation: {attenuation:.2f} dB")
            framework.print_output(f"   📍 Distance: {scenario['distance']} m")

    print()


def example_4_programmatic_events():
    """Example 4: Programmatic communication with events"""
    print("⚡ Example 4: Programmatic Communication with Events")
    print("-" * 50)

    framework = ArcherFramework()

    # Create programmatic communicator
    prog_comm = create_communicator(CommunicationType.PROGRAMMATIC)
    framework.register_communicator(CommunicationType.PROGRAMMATIC, prog_comm)

    # Event handlers
    def handle_user_input(message: CommunicationMessage):
        framework.print_output(f"🎯 User Input Handler: {message.content}")

    def handle_system_event(message: CommunicationMessage):
        framework.print_output(f"🔧 System Event Handler: {message.content}")

    def handle_error(message: CommunicationMessage):
        framework.print_output(f"❌ Error Handler: {message.content}")

    # Register event handlers
    prog_comm.register_handler("user_input", handle_user_input)
    prog_comm.register_handler("system_event", handle_system_event)
    prog_comm.register_handler("error", handle_error)

    # Send different types of events
    events = [
        CommunicationMessage(
            content="User clicked button",
            sender="ui",
            receiver="controller",
            message_type=CommunicationType.PROGRAMMATIC,
            metadata={"event_type": "user_input"},
        ),
        CommunicationMessage(
            content="System startup complete",
            sender="system",
            receiver="monitor",
            message_type=CommunicationType.PROGRAMMATIC,
            metadata={"event_type": "system_event"},
        ),
        CommunicationMessage(
            content="Database connection failed",
            sender="db_manager",
            receiver="error_handler",
            message_type=CommunicationType.PROGRAMMATIC,
            metadata={"event_type": "error"},
        ),
    ]

    for event in events:
        result = framework.send_message(event)
        framework.print_output(f"✅ Event sent: {result.message}")
        time.sleep(0.1)  # Allow time for event processing

    print()


def example_5_performance_monitoring():
    """Example 5: Performance monitoring and metrics"""
    print("📊 Example 5: Performance Monitoring and Metrics")
    print("-" * 45)

    framework = ArcherFramework()

    # Register multiple communicators
    communicators = {
        CommunicationType.INTERPROCESS: create_communicator(
            CommunicationType.INTERPROCESS, {"method": "queue"}
        ),
        CommunicationType.PSYCHOLOGICAL: create_communicator(
            CommunicationType.PSYCHOLOGICAL, {"style": "assertive"}
        ),
        CommunicationType.PHYSICS: create_communicator(
            CommunicationType.PHYSICS, {"medium": "fiber"}
        ),
        CommunicationType.PROGRAMMATIC: create_communicator(
            CommunicationType.PROGRAMMATIC
        ),
    }

    for comm_type, comm in communicators.items():
        framework.register_communicator(comm_type, comm)

    # Send multiple messages to generate metrics
    framework.print_output("🔄 Sending multiple messages to generate metrics...")

    for i in range(10):
        for comm_type in communicators.keys():
            message = CommunicationMessage(
                content=f"Test message {i}",
                sender="test_sender",
                receiver="test_receiver",
                message_type=comm_type,
                priority=5,
            )
            framework.send_message(message)

    # Analyze performance
    framework.print_output("\n📈 Performance Analysis:")
    metrics = framework.get_metrics()

    for comm_type in communicators.keys():
        type_name = comm_type.value
        avg_response = metrics.get(f"{type_name}_avg_response", 0)
        success_rate = metrics.get(f"{type_name}_success_rate", 0)

        framework.print_output(f"\n🔍 {type_name.upper()} Communication:")
        framework.print_output(f"   ⏱️  Average Response Time: {avg_response:.4f}s")
        framework.print_output(f"   ✅ Success Rate: {success_rate:.2%}")
        framework.print_output(
            f"   📊 Total Messages: {len([m for m in framework.message_history if m.message_type == comm_type])}"
        )

    # Overall statistics
    framework.print_output("\n📋 Overall Statistics:")
    framework.print_output(
        f"   📨 Total Messages Sent: {len(framework.message_history)}"
    )
    framework.print_output(f"   🎯 Active Communicators: {len(framework.communicators)}")
    framework.print_output(f"   📊 Metrics Tracked: {len(metrics)}")

    print()


def example_6_error_handling():
    """Example 6: Comprehensive error handling"""
    print("🛡️ Example 6: Comprehensive Error Handling")
    print("-" * 42)

    framework = ArcherFramework()

    # Test various error scenarios
    error_scenarios = [
        {
            "name": "Unregistered communicator type",
            "message": CommunicationMessage(
                content="Test",
                sender="test",
                receiver="test",
                message_type=CommunicationType.NETWORK,  # Not registered
            ),
        },
        {
            "name": "Network connection failure",
            "setup": lambda: framework.register_communicator(
                CommunicationType.NETWORK,
                create_communicator(
                    CommunicationType.NETWORK, {"host": "invalid_host", "port": 9999}
                ),
            ),
            "message": CommunicationMessage(
                content="Network test",
                sender="client",
                receiver="server",
                message_type=CommunicationType.NETWORK,
            ),
        },
        {
            "name": "Serial port not available",
            "setup": lambda: framework.register_communicator(
                CommunicationType.SERIAL,
                create_communicator(CommunicationType.SERIAL, {"port": "INVALID_PORT"}),
            ),
            "message": CommunicationMessage(
                content="Serial test",
                sender="device",
                receiver="controller",
                message_type=CommunicationType.SERIAL,
            ),
        },
    ]

    for scenario in error_scenarios:
        framework.print_output(f"\n❌ Testing: {scenario['name']}")

        # Reset framework for clean test
        framework = ArcherFramework()

        if "setup" in scenario:
            scenario["setup"]()

        result = framework.send_message(scenario["message"])

        framework.print_output(
            f"   Status: {'✅ Success' if result.success else '❌ Failed'}"
        )
        framework.print_output(f"   Message: {result.message}")
        if result.error_code:
            framework.print_output(f"   Error Code: {result.error_code}")
        framework.print_output(f"   Response Time: {result.response_time:.4f}s")

    print()


def main():
    """Run all examples"""
    print("🤖 Archer Framework - Comprehensive Examples")
    print("=" * 60)
    print()

    examples = [
        example_1_basic_messaging,
        example_2_psychological_communication,
        example_3_physics_signal_simulation,
        example_4_programmatic_events,
        example_5_performance_monitoring,
        example_6_error_handling,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Example failed: {str(e)}")

        print("\n" + "=" * 60 + "\n")

    print("🎯 All examples completed!")
    print("\n💡 Key Takeaways:")
    print("   • Archer Framework provides unified communication across domains")
    print("   • Built-in performance monitoring and error handling")
    print("   • Extensible architecture for custom communication types")
    print("   • Psychological analysis adds intelligence to communication")
    print("   • Physics simulation enables signal transmission modeling")
    print("   • Event-driven programming support for reactive systems")


if __name__ == "__main__":
    main()
