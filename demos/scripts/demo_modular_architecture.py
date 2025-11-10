# ----------------------------------------------------------------------
# Demonstration of the modular Echoes Assistant V2
# ----------------------------------------------------------------------
import json

from echoes import EchoesAssistantV2, RuntimeOptions


def demo_basic_usage():
    """Demonstrate basic assistant usage."""
    print("🤖 Echoes Assistant V2 - Basic Usage Demo")
    print("=" * 50)

    # Create assistant with minimal configuration
    opts = RuntimeOptions(
        enable_rag=False,  # Disable for demo to avoid dependencies
        enable_glimpse=False,
        enable_multimodal=False,
        enable_legal=False,
    )

    assistant = EchoesAssistantV2(opts=opts)

    # Test basic chat
    response = assistant.chat(
        "Hello! Can you explain what you are in one sentence?", stream=False
    )
    print(f"Assistant: {response}")

    # Show stats
    stats = assistant.get_stats()
    print(f"\n📊 Stats: {json.dumps(stats, indent=2)}")


def demo_knowledge_management():
    """Demonstrate knowledge management features."""
    print("\n🧠 Knowledge Management Demo")
    print("=" * 40)

    assistant = EchoesAssistantV2()

    # Add some knowledge
    assistant.add_knowledge("echoes_version", "2.0.0", {"type": "metadata"})
    assistant.add_knowledge("architecture", "modular", {"type": "design"})

    # Retrieve knowledge
    version = assistant.knowledge_manager.get_knowledge("echoes_version")
    print(f"Version: {version}")

    # Search knowledge
    results = assistant.knowledge_manager.search_knowledge("design")
    print(f"Search results: {results}")


def demo_filesystem_tools():
    """Demonstrate filesystem tools."""
    print("\n📁 Filesystem Tools Demo")
    print("=" * 35)

    assistant = EchoesAssistantV2()

    # List files in current directory
    files = assistant.fs_tools.list_files(".", "*.py")
    print(f"Python files: {len(files)} found")

    # Create a test file
    test_content = "Hello from Echoes Assistant V2!"
    success = assistant.fs_tools.write_file("demo_test.txt", test_content)
    print(f"Write file: {'✅' if success else '❌'}")

    # Read the file back
    if success:
        content = assistant.fs_tools.read_file("demo_test.txt")
        print(f"Read content: {content}")

        # Clean up
        assistant.fs_tools.delete_file("demo_test.txt")
        print("Cleaned up test file")


def demo_inventory_system():
    """Demonstrate ATLAS-style inventory system."""
    print("\n📦 Inventory System Demo")
    print("=" * 35)

    assistant = EchoesAssistantV2()

    # Use unique SKUs with timestamp to avoid conflicts
    import time

    timestamp = int(time.time())

    # Add items to inventory
    item1 = assistant.inventory_service.add_item(
        sku=f"ECHOES-{timestamp}-001",
        name="Assistant Core",
        category="Software",
        quantity=1,
        location="Main Server",
    )

    item2 = assistant.inventory_service.add_item(
        sku=f"ECHOES-{timestamp}-002",
        name="Knowledge Base",
        category="Data",
        quantity=1000,
        location="Cloud Storage",
    )

    print(f"Added items: {item1.name}, {item2.name}")

    # Search inventory
    items = assistant.inventory_service.search_items("Assistant")
    print(f"Found {len(items)} items matching 'Assistant'")


def demo_quantum_states():
    """Demonstrate quantum state management."""
    print("\n⚛️  Quantum State Demo")
    print("=" * 30)

    assistant = EchoesAssistantV2()

    # Get quantum metrics
    metrics = assistant.quantum_state_manager.get_quantum_metrics()
    print(f"Quantum metrics: {json.dumps(metrics, indent=2)}")

    # Perform a measurement
    result = assistant.quantum_state_manager.measure_state("superposition")
    print(f"Measurement result: {result}")


def demo_modular_architecture():
    """Demonstrate the modular architecture benefits."""
    print("\n🏗️  Modular Architecture Demo")
    print("=" * 40)

    # Show how easy it is to customize
    opts_custom = RuntimeOptions(
        enable_rag=False,  # Disable RAG for faster startup
        enable_glimpse=False,  # Disable pre-flight checks
        enable_tools=False,  # Disable tool framework
        enable_status=True,  # Keep status indicators
        model="gpt-4o-mini",  # Use smaller model
    )

    print("Creating lightweight assistant...")
    lightweight_assistant = EchoesAssistantV2(opts=opts_custom)

    # Show it still works for basic chat
    response = lightweight_assistant.chat(
        "What are the benefits of modular architecture?", stream=False
    )
    print(f"Lightweight assistant response: {response[:100]}...")


def main():
    """Run all demonstrations."""
    print("🚀 Echoes Assistant V2 - Modular Architecture Demo")
    print("=" * 60)

    try:
        demo_basic_usage()
        demo_knowledge_management()
        demo_filesystem_tools()
        demo_inventory_system()
        demo_quantum_states()
        demo_modular_architecture()

        print("\n✅ All demos completed successfully!")
        print("\n🎯 Key Benefits Demonstrated:")
        print("  • Modular, testable architecture")
        print("  • Graceful fallbacks for missing dependencies")
        print("  • Easy customization via RuntimeOptions")
        print("  • Clean separation of concerns")
        print("  • Production-ready error handling")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
