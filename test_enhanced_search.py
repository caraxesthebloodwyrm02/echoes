#!/usr/bin/env python3
"""Test enhanced web search functionality."""

from assistant_v2_core import EchoesAssistantV2

def test_enhanced_search():
    """Test the enhanced web search with better fallbacks."""
    
    print("=" * 60)
    print("🔍 Enhanced Web Search Test")
    print("=" * 60)
    
    # Initialize assistant
    print("\n📦 Initializing assistant with enhanced web search...")
    assistant = EchoesAssistantV2(
        enable_tools=True,
        enable_rag=False,
        session_id="enhanced_search_test"
    )
    
    print(f"✅ Assistant ready with {len(assistant.list_tools())} tools")
    
    # Test web search directly
    print("\n🔍 Testing enhanced web search...")
    try:
        result = assistant.tool_registry.execute(
            'web_search',
            query="OpenAI function calling documentation",
            max_results=3
        )
        
        if result.success:
            print(f"✅ Search successful!")
            print(f"   Query: {result.data['query']}")
            print(f"   Results found: {result.data['total_results']}")
            
            for i, res in enumerate(result.data['results'], 1):
                print(f"\n   {i}. {res['title']}")
                print(f"      URL: {res['url']}")
                print(f"      Snippet: {res['snippet'][:100]}...")
                print(f"      Source: {res['source']}")
        else:
            print(f"❌ Search failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test interactive search
    print("\n💬 Testing interactive web search...")
    try:
        response = assistant.chat(
            "Search for information about Python async programming and summarize the key points",
            stream=False
        )
        print(f"✅ Response generated: {len(response)} characters")
        print(f"Preview: {response[:300]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📋 Search Provider Information")
    print("=" * 60)
    print("\n🔧 To get REAL search results (not simulated):")
    print("\n1. Tavily API (Recommended):")
    print("   - Get API key from https://tavily.com")
    print("   - Set environment variable: TAVILY_API_KEY=your_key")
    
    print("\n2. Serper API (Google Search):")
    print("   - Get API key from https://serper.dev")
    print("   - Set environment variable: SERPER_API_KEY=your_key")
    
    print("\n3. Brave Search API:")
    print("   - Get API key from https://brave.com/search/api")
    print("   - Set environment variable: BRAVE_SEARCH_API_KEY=your_key")
    
    print("\n⚠️  Without API keys, the system uses simulated results for testing.")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_search()
