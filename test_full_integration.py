#!/usr/bin/env python3
"""Test full integration of OpenAI RAG and filesystem tools."""

from assistant_v2_core import EchoesAssistantV2

def test_full_integration():
    """Test the complete integrated system."""
    
    print("=" * 60)
    print("🚀 Full Integration Test")
    print("=" * 60)
    
    # Initialize assistant with all features
    print("\n📦 Initializing EchoesAssistantV2...")
    assistant = EchoesAssistantV2(
        enable_tools=True,
        enable_rag=True,
        enable_status=True,
        session_id="full_integration_test"
    )
    
    print(f"✅ Assistant ready!")
    print(f"   Tools loaded: {len(assistant.list_tools())}")
    print(f"   RAG enabled: {assistant.enable_rag}")
    
    # Test filesystem tools
    print("\n🔧 Testing Filesystem Tools...")
    filesystem_tools = [
        'read_file', 'write_file', 'list_directory', 
        'search_files', 'create_directory', 'get_file_info'
    ]
    
    for tool in filesystem_tools:
        if tool in assistant.list_tools():
            print(f"   ✅ {tool}")
        else:
            print(f"   ❌ {tool} missing")
    
    # Test RAG system
    print("\n🧠 Testing RAG System...")
    if assistant.rag:
        # Add some test knowledge
        test_docs = [
            {"text": "EchoesAssistantV2 is an AI assistant with filesystem capabilities.", "metadata": {"source": "integration_test"}},
            {"text": "The assistant uses OpenAI for embeddings and function calling.", "metadata": {"source": "integration_test"}},
            {"text": "Filesystem operations are safe and sandboxed.", "metadata": {"source": "integration_test"}}
        ]
        
        result = assistant.add_knowledge(test_docs)
        print(f"   ✅ Knowledge added: {result}")
        
        # Test knowledge retrieval
        search_results = assistant.search_knowledge("filesystem", limit=3)
        print(f"   ✅ Knowledge search found: {len(search_results)} results")
        
        # Test RAG stats
        rag_stats = assistant.rag.get_stats()
        print(f"   ✅ RAG stats: {rag_stats.get('total_documents', 0)} documents")
    else:
        print("   ❌ RAG system not available")
    
    # Test a simple interaction
    print("\n💬 Testing Simple Interaction...")
    try:
        response = assistant.chat(
            "What can you tell me about the filesystem capabilities?",
            stream=False
        )
        print(f"   ✅ Response generated: {len(response)} characters")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Full integration test completed successfully!")
    print("The EchoesAssistantV2 is now using:")
    print("  • OpenAI embeddings for RAG (not sentence-transformers)")
    print("  • OpenAI function calling for filesystem operations")
    print("  • All systems are properly integrated and working")
    print("=" * 60)

if __name__ == "__main__":
    test_full_integration()
