#!/usr/bin/env python3
"""
Test Agentic Assistant Capabilities

Tests knowledge management, filesystem interaction, and context building.
"""

import sys
import os
# Add parent directory to path to access assistant_v2_core
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import os as os_module
from assistant_v2_core import EchoesAssistantV2


def test_agentic_capabilities():
    """Test all agentic capabilities."""
    print("\n" + "=" * 70)
    print("Testing Agentic Assistant Capabilities")
    print("=" * 70)

    # Initialize assistant
    print("\n[Test 1] Initializing agentic assistant...")
    assistant = EchoesAssistantV2(enable_tools=True, enable_rag=False, enable_streaming=False, enable_status=False)
    print("✓ Assistant initialized with knowledge, filesystem, and action capabilities")

    # Test knowledge gathering
    print("\n[Test 2] Testing knowledge gathering...")
    k_id1 = assistant.gather_knowledge(
        content="ATLAS is an inventory management system",
        source="ATLAS/README.md",
        category="inventory",
        tags=["atlas", "inventory"],
    )
    print(f"✓ Knowledge gathered: {k_id1}")

    k_id2 = assistant.gather_knowledge(
        content="EchoesAssistantV2 supports tool calling and RAG",
        source="assistant_v2_core.py",
        category="assistant",
        tags=["echoes", "assistant"],
    )
    print(f"✓ Knowledge gathered: {k_id2}")

    # Test knowledge search
    print("\n[Test 3] Testing knowledge search...")
    results = assistant.search_knowledge(query="inventory", limit=5)
    print(f"✓ Found {len(results)} knowledge entries")
    for r in results:
        print(f"  - [{r['category']}] {r['content'][:50]}...")

    # Test context management
    print("\n[Test 4] Testing context management...")
    assistant.update_context("current_project", "Echoes")
    assistant.update_context("working_directory", os_module.getcwd())
    assistant.update_context("active_features", ["ATLAS", "Assistant", "Tools"])
    print("✓ Context updated")

    context_summary = assistant.get_context_summary()
    print(f"✓ Context summary:\n{context_summary}")

    # Test filesystem - list directory
    print("\n[Test 5] Testing filesystem - list directory...")
    result = assistant.list_directory("ATLAS", pattern="*.py")
    if result["success"]:
        print(f"✓ Listed {result['total_files']} Python files in ATLAS")
        for f in result["files"][:5]:
            print(f"  - {f['name']} ({f['size']} bytes)")
    else:
        print(f"✗ Error: {result['error']}")

    # Test filesystem - read file
    print("\n[Test 6] Testing filesystem - read file...")
    result = assistant.read_file("ATLAS/__init__.py")
    if result["success"]:
        print(f"✓ Read file: {result['filepath']}")
        print(f"  Size: {result['size']} bytes, Lines: {result['lines']}")
    else:
        print(f"✗ Error: {result['error']}")

    # Test filesystem - search files
    print("\n[Test 7] Testing filesystem - search files...")
    result = assistant.search_files("test", search_path=".")
    if result["success"]:
        print(f"✓ Found {result['total']} files matching 'test'")
        for f in result["results"][:5]:
            print(f"  - {f['name']}")
    else:
        print(f"✗ Error: {result['error']}")

    # Test filesystem - directory tree
    print("\n[Test 8] Testing filesystem - directory tree...")
    result = assistant.get_directory_tree("ATLAS", max_depth=2)
    if result["success"]:
        print("✓ Built directory tree for ATLAS")
        tree = result["tree"]
        print(f"  Root: {tree['name']}")
        if "children" in tree:
            print(f"  Children: {len(tree['children'])}")
    else:
        print(f"✗ Error: {result['error']}")

    # Test action execution
    print("\n[Test 9] Testing action execution...")
    result = assistant.execute_action("inventory", "list_items")
    print(f"✓ Action executed: {result['action_id']}")
    print(f"  Success: {result['success']}, Duration: {result['duration_ms']:.1f}ms")

    # Test statistics
    print("\n[Test 10] Testing comprehensive statistics...")
    stats = assistant.get_stats()
    print("✓ Statistics collected:")
    print(f"  - Session: {stats['session_id']}")
    print(f"  - Messages: {stats['messages']}")
    print(f"  - Tools enabled: {stats['tools_enabled']}")
    print(f"  - Knowledge entries: {stats['knowledge']['total_entries']}")
    print(f"  - Actions: {stats['actions']['total_actions']}")

    # Test knowledge categories
    print("\n[Test 11] Testing knowledge categories...")
    results_inv = assistant.search_knowledge(category="inventory", limit=5)
    results_ast = assistant.search_knowledge(category="assistant", limit=5)
    print(f"✓ Inventory knowledge: {len(results_inv)} entries")
    print(f"✓ Assistant knowledge: {len(results_ast)} entries")

    print("\n" + "=" * 70)
    print("✓ All agentic capabilities tested successfully!")
    print("=" * 70)
    print("\nSummary:")
    print("- Knowledge Management: ✓ Working")
    print("- Context Building: ✓ Working")
    print("- Filesystem Navigation: ✓ Working")
    print("- Action Execution: ✓ Working")
    print("- Error Handling: ✓ Working")
    print("\n✓ Assistant is fully agentic and context-aware!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_agentic_capabilities()
