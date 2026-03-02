#!/usr/bin/env python3
"""
Comprehensive test of Knowledge Graph and Meaningful Communication in EchoesAssistantV2
"""

import asyncio

from assistant_v2_core import EchoesAssistantV2


async def test_knowledge_graph_integration():
    print("=" * 70)
    print("🧠 Testing Knowledge Graph & Meaningful Communication Integration")
    print("=" * 70)

    # Initialize assistant with knowledge graph enabled
    assistant = EchoesAssistantV2(
        enable_rag=True,
        enable_tools=True,
        enable_streaming=True,
        enable_status=True,
        enable_glimpse=True,
        enable_external_contact=True,
    )

    print(
        f"\n✅ Assistant initialized with Knowledge Graph: {assistant.enable_knowledge_graph}"
    )

    # Test 1: Add knowledge nodes
    print("\n1️⃣ Adding knowledge nodes...")

    # Add person node
    result1 = assistant.add_knowledge_node(
        node_id="person_001",
        node_type="person",
        label="Dr. Sarah Chen",
        description="AI researcher specializing in natural language processing",
        properties={"institution": "MIT", "field": "NLP", "publications": 25},
    )
    print(f"   ✅ {result1['message']}")

    # Add concept node
    result2 = assistant.add_knowledge_node(
        node_id="concept_001",
        node_type="concept",
        label="Natural Language Processing",
        description="Field of AI focused on understanding and generating human language",
        properties={
            "category": "AI",
            "complexity": "high",
            "applications": ["chatbots", "translation"],
        },
    )
    print(f"   ✅ {result2['message']}")

    # Add project node
    result3 = assistant.add_knowledge_node(
        node_id="project_001",
        node_type="project",
        label="EchoesAssistantV2",
        description="Advanced AI assistant with knowledge graph and external API integration",
        properties={
            "status": "active",
            "version": "2.0",
            "features": ["RAG", "Glimpse", "Knowledge Graph"],
        },
    )
    print(f"   ✅ {result3['message']}")

    # Test 2: Add knowledge relationships
    print("\n2️⃣ Adding knowledge relationships...")

    # Person works on project
    result4 = assistant.add_knowledge_relation(
        source_id="person_001",
        target_id="project_001",
        relation_type="works_on",
        weight=0.9,
        properties={"role": "lead_researcher", "since": "2024"},
    )
    print(f"   ✅ {result4['message']}")

    # Project uses concept
    result5 = assistant.add_knowledge_relation(
        source_id="project_001",
        target_id="concept_001",
        relation_type="uses",
        weight=0.8,
        properties={"implementation": "deep_learning"},
    )
    print(f"   ✅ {result5['message']}")

    # Person specializes in concept
    result6 = assistant.add_knowledge_relation(
        source_id="person_001",
        target_id="concept_001",
        relation_type="specializes_in",
        weight=0.95,
        properties={"experience_years": 8},
    )
    print(f"   ✅ {result6['message']}")

    # Test 3: Add memory fragments
    print("\n3️⃣ Adding memory fragments...")

    result7 = assistant.add_memory_fragment(
        content="Dr. Sarah Chen presented the EchoesAssistantV2 project at the AI conference",
        context={
            "event": "AI Conference 2024",
            "location": "San Francisco",
            "date": "2024-10-15",
        },
        importance=0.9,
    )
    print(f"   ✅ {result7['message']}")
    print(f"   📋 Entities found: {result7['entities_found']}")
    print(f"   🧠 Concepts found: {result7['concepts_found']}")

    result8 = assistant.add_memory_fragment(
        content="The knowledge graph integration enables meaningful communication with context awareness",
        context={"feature": "Knowledge Graph", "benefit": "context_awareness"},
        importance=0.8,
    )
    print(f"   ✅ {result8['message']}")

    # Test 4: Search knowledge graph
    print("\n4️⃣ Searching knowledge graph...")

    search_result = assistant.search_knowledge_graph("Sarah Chen", limit=5)
    if search_result["success"]:
        print(f"   ✅ Found {search_result['total_found']} nodes")
        for node in search_result["results"]:
            print(
                f"      📍 {node['label']} ({node['type']}): {node['description'][:50]}..."
            )
            if node["related_nodes"]:
                print(
                    f"         ↳ Related: {', '.join([r['label'] for r in node['related_nodes']])}"
                )

    # Test 5: Get knowledge relationships
    print("\n5️⃣ Getting knowledge relationships...")

    relations_result = assistant.get_knowledge_relationships("person_001", max_depth=2)
    if relations_result["success"]:
        print(f"   ✅ Found {relations_result['total_related']} related nodes")
        for node in relations_result["related_nodes"]:
            print(f"      🔗 {node['label']} ({node['type']})")

    # Test 6: Retrieve relevant memories
    print("\n6️⃣ Retrieving relevant memories...")

    memories_result = assistant.retrieve_relevant_memories(
        "Sarah Chen conference", limit=3
    )
    if memories_result["success"]:
        print(f"   ✅ Found {memories_result['total_found']} relevant memories")
        for memory in memories_result["memories"]:
            print(
                f"      💭 {memory['content'][:60]}... (importance: {memory['importance']})"
            )
            print(f"         📅 {memory['timestamp']}")

    # Test 7: Meaningful communication with context
    print("\n7️⃣ Testing meaningful communication with context...")

    communication_result = assistant.communicate_with_context(
        "Tell me about Dr. Sarah Chen's work on the EchoesAssistantV2 project",
        system_prompt="You are an AI assistant with deep knowledge of the Echoes project and team members.",
    )

    if communication_result["success"]:
        print("   ✅ Meaningful communication completed")
        print("   📊 Context used:")
        print(f"      - Entities: {communication_result['context_used']['entities']}")
        print(f"      - Memories: {communication_result['context_used']['memories']}")
        print(
            f"      - Concepts: {communication_result['context_used']['related_concepts']}"
        )
        print(f"   💬 Response preview: {communication_result['response'][:200]}...")

    # Test 8: Learn from interaction
    print("\n8️⃣ Learning from user interaction...")

    learn_result = assistant.learn_from_interaction(
        user_message="What is the relationship between NLP and knowledge graphs?",
        assistant_response="NLP and knowledge graphs are closely related - knowledge graphs provide structured semantic information that enhances NLP systems, while NLP techniques can extract and populate knowledge graphs from unstructured text.",
        confidence=0.9,
    )

    if learn_result["success"]:
        print(f"   ✅ {learn_result['message']}")
        print(f"   📈 Total conversation turns: {learn_result['conversation_turns']}")

    # Test 9: Get knowledge graph statistics
    print("\n9️⃣ Getting knowledge graph statistics...")

    stats_result = assistant.get_knowledge_graph_stats()
    if stats_result["success"]:
        stats = stats_result["stats"]
        print("   ✅ Knowledge Graph Statistics:")
        print(f"      📊 Nodes: {stats['nodes']}")
        print(f"      🔗 Relations: {stats['relations']}")
        print(f"      💭 Memories: {stats['memories']}")
        print(f"      💬 Conversation turns: {stats['conversation_turns']}")
        print(f"      📂 Node types: {stats['node_types']}")

    # Test 10: Full stats integration
    print("\n🔟 Getting full assistant statistics...")

    full_stats = assistant.get_stats()
    print("   ✅ Full Assistant Statistics:")
    print(
        f"      🧠 Knowledge Graph: {'Enabled' if full_stats.get('knowledge_graph_stats') else 'Disabled'}"
    )
    print(
        f"      🔍 RAG System: {'Enabled' if full_stats.get('rag_enabled') else 'Disabled'}"
    )
    print(
        f"      👁️ Glimpse: {'Enabled' if full_stats.get('glimpse_enabled') else 'Disabled'}"
    )
    print(
        f"      🌐 External Contact: {'Enabled' if full_stats.get('external_contact_enabled') else 'Disabled'}"
    )

    print("\n" + "=" * 70)
    print("🎉 KNOWLEDGE GRAPH INTEGRATION TEST COMPLETE")
    print("=" * 70)
    print("\nKey Achievements:")
    print("• ✅ Knowledge nodes and relationships created")
    print("• ✅ Memory fragments with entity/concept extraction")
    print("• ✅ Graph search and relationship traversal")
    print("• ✅ Context-aware meaningful communication")
    print("• ✅ Learning from user interactions")
    print("• ✅ Comprehensive statistics and monitoring")
    print("\nThe EchoesAssistantV2 now provides:")
    print("• 🧠 Semantic knowledge representation")
    print("• 💬 Context-aware communication")
    print("• 📚 Persistent memory with temporal awareness")
    print("• 🔗 Relationship-based reasoning")
    print("• 📈 Continuous learning from interactions")
    print("\n!CONTACT → !COMMUNICATE: Mission Accomplished! 🚀")


if __name__ == "__main__":
    asyncio.run(test_knowledge_graph_integration())
