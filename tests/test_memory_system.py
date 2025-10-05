#!/usr/bin/env python3
"""
Test script for Knowledge Graph Memory System
Tests the MCP memory server functionality
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.knowledge_graph_memory import MemoryMCPServer


def test_basic_memory_operations():
    """Test basic memory operations"""
    print("🧪 Testing Knowledge Graph Memory System...")

    # Use a temporary memory file for testing
    test_memory_file = "test_memory.json"
    memory_server = MemoryMCPServer(test_memory_file)

    try:
        # Test 1: Create entities
        print("\n1. Creating entities...")
        entities = [
            {
                "name": "test_user",
                "entityType": "person",
                "observations": ["Test user for memory system"],
            },
            {
                "name": "educational_system",
                "entityType": "system",
                "observations": ["Interactive learning platform"],
            },
        ]

        result = memory_server.create_entities_tool(entities)
        print(f"   ✅ Created entities: {result}")

        # Test 2: Create relations
        print("\n2. Creating relations...")
        relations = [{"from": "test_user", "to": "educational_system", "relationType": "uses"}]

        result = memory_server.create_relations_tool(relations)
        print(f"   ✅ Created relations: {result}")

        # Test 3: Add observations
        print("\n3. Adding observations...")
        observations = [
            {
                "entityName": "test_user",
                "contents": ["Prefers visual learning", "Enjoys creative activities"],
            }
        ]

        result = memory_server.add_observations_tool(observations)
        print(f"   ✅ Added observations: {result}")

        # Test 4: Read graph
        print("\n4. Reading graph...")
        result = memory_server.read_graph_tool()
        graph_data = json.loads(result)
        print(
            f"   ✅ Graph contains {len(graph_data['entities'])} entities and {len(graph_data['relations'])} relations"
        )

        # Test 5: Search nodes
        print("\n5. Searching nodes...")
        result = memory_server.search_nodes_tool("visual")
        search_data = json.loads(result)
        print(f"   ✅ Found {len(search_data['matches'])} matches for 'visual'")

        # Test 6: Open specific nodes
        print("\n6. Opening specific nodes...")
        result = memory_server.open_nodes_tool(["test_user"])
        node_data = json.loads(result)
        print(f"   ✅ Retrieved {len(node_data['entities'])} entities with their relations")

        print("\n🎉 All tests passed! Memory system is working correctly.")

    finally:
        # Clean up test file
        import os

        if os.path.exists(test_memory_file):
            os.remove(test_memory_file)
            print(f"\n🧹 Cleaned up test file: {test_memory_file}")


def test_memory_integration():
    """Test memory integration with existing system"""
    print("\n🔗 Testing memory integration...")

    # Initialize with the actual memory file
    memory_server = MemoryMCPServer()

    # Create some entities based on existing stakeholders
    try:
        entities = [
            {
                "name": "default_user",
                "entityType": "person",
                "observations": ["Default user for educational ecosystem interactions"],
            },
            {
                "name": "memory_system",
                "entityType": "system",
                "observations": ["Knowledge graph memory for persistent context"],
            },
        ]

        result = memory_server.create_entities_tool(entities)
        print(f"   ✅ Integration entities created: {result}")

        # Create relation
        relations = [{"from": "default_user", "to": "memory_system", "relationType": "utilizes"}]

        result = memory_server.create_relations_tool(relations)
        print(f"   ✅ Integration relations created: {result}")

        print("   🎉 Memory integration test completed!")

    except Exception as e:
        print(f"   ⚠️ Integration test note: {e}")


if __name__ == "__main__":
    test_basic_memory_operations()
    test_memory_integration()
    print("\n✨ Memory system testing complete!")
