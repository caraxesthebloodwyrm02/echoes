#!/usr/bin/env python3
"""Test web search integration with EchoesAssistantV2."""

from assistant_v2_core import EchoesAssistantV2

def test_web_search_integration():
    """Test the web search capabilities."""
    
    print("=" * 60)
    print("🌐 Web Search Integration Test")
    print("=" * 60)
    
    # Initialize assistant with web search tools
    print("\n📦 Initializing EchoesAssistantV2 with web search...")
    assistant = EchoesAssistantV2(
        enable_tools=True,
        enable_rag=False,  # Disable RAG to focus on web search
        session_id="web_search_test"
    )
    
    print(f"✅ Assistant ready!")
    print(f"   Total tools loaded: {len(assistant.list_tools())}")
    
    # Check for web search tools
    print("\n🔧 Checking Web Search Tools...")
    web_tools = ['web_search', 'get_web_page_content']
    
    for tool in web_tools:
        if tool in assistant.list_tools():
            print(f"   ✅ {tool}")
        else:
            print(f"   ❌ {tool} missing")
    
    # Test web search directly
    print("\n🔍 Testing Web Search Tool...")
    try:
        result = assistant.tool_registry.execute(
            'web_search',
            query="latest AI developments 2025",
            max_results=3
        )
        
        if result.success:
            print(f"   ✅ Search successful: {result.data['total_results']} results")
            for i, res in enumerate(result.data['results'][:2], 1):
                print(f"      {i}. {res['title'][:50]}...")
                print(f"         {res['url']}")
        else:
            print(f"   ❌ Search failed: {result.error}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test a simple interaction with web search
    print("\n💬 Testing Interactive Web Search...")
    try:
        response = assistant.chat(
            "Search for information about OpenAI's latest features and summarize what you find",
            stream=False
        )
        print(f"   ✅ Response generated: {len(response)} characters")
        # Show first 200 characters
        print(f"   Preview: {response[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Web search integration test completed!")
    print("\n📋 Available Web Search Capabilities:")
    print("  • General web search via DuckDuckGo (no API key required)")
    print("  • Optional Brave Search API support")
    print("  • Optional Google Custom Search API support")
    print("  • Web page content extraction")
    print("  • Safe search filtering")
    print("\n🔧 To use premium search providers:")
    print("  • Set BRAVE_SEARCH_API_KEY for Brave Search")
    print("  • Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID for Google")
    print("  • Set SEARCH_PROVIDER environment variable to choose provider")
    print("=" * 60)

if __name__ == "__main__":
    test_web_search_integration()
