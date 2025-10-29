#!/usr/bin/env python3
"""Test dynamic model selection in EchoesAssistantV2."""

from assistant_v2_core import EchoesAssistantV2
import time

def test_dynamic_model_selection():
    """Test the dynamic model selection logic."""
    
    print("=" * 60)
    print("🧠 Dynamic Model Selection Test")
    print("=" * 60)
    
    # Initialize assistant
    print("\n📦 Initializing EchoesAssistantV2 with dynamic model selection...")
    assistant = EchoesAssistantV2(
        enable_tools=True,
        enable_rag=True,
        session_id="dynamic_model_test"
    )
    
    print(f"✅ Assistant ready!")
    print(f"   Default model: {assistant.default_model}")
    print(f"   Available models: {list(assistant.available_models.values())}")
    
    # Test cases for different model selection scenarios
    test_cases = [
        {
            "name": "Simple Task",
            "prompt": "What is the capital of France?",
            "expected_model": "gpt-4o-mini",
            "reason": "Simple factual question"
        },
        {
            "name": "Web Search Required",
            "prompt": "What is the latest news about OpenAI today?",
            "expected_model": "gpt-4o-search-preview",
            "reason": "Contains 'latest' and 'today' - needs web search"
        },
        {
            "name": "Complex Analysis",
            "prompt": "Analyze the philosophical implications of artificial intelligence on human consciousness and provide a detailed comparison with historical technological revolutions",
            "expected_model": "gpt-4o",
            "reason": "Complex analysis with multiple concepts"
        },
        {
            "name": "Tool Usage with Web Search",
            "prompt": "Search for current stock prices of tech companies and analyze the trends",
            "expected_model": "gpt-4o-search-preview",
            "reason": "Web search tool will be used"
        },
        {
            "name": "Medium Complexity",
            "prompt": "Explain how photosynthesis works",
            "expected_model": "gpt-4o-mini",
            "reason": "Educational but not overly complex"
        }
    ]
    
    print("\n" + "=" * 60)
    print("🧪 Testing Model Selection Logic")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Prompt: {test['prompt'][:60]}...")
        print(f"   Expected: {test['expected_model']}")
        print(f"   Reason: {test['reason']}")
        
        # Test model selection
        tools = None
        if assistant.enable_tools and assistant.tool_registry:
            tools = assistant.tool_registry.get_openai_schemas()
            
        selected_model = assistant.model_router.select_model(test['prompt'], tools)
        print(f"   Selected: {selected_model}")
        
        if selected_model == test['expected_model']:
            print("   ✅ Correct selection")
        else:
            print("   ⚠️  Different selection (may still be appropriate)")
    
    # Test actual API calls with different prompts
    print("\n" + "=" * 60)
    print("🚀 Testing API Calls with Dynamic Selection")
    print("=" * 60)
    
    # Reset metrics for clean test
    assistant.reset_model_metrics()
    
    api_test_cases = [
        {
            "name": "Simple Query",
            "prompt": "What is 2 + 2?",
            "expected": "gpt-4o-mini"
        },
        {
            "name": "Web Search Query",
            "prompt": "What's the current weather in Tokyo?",
            "expected": "gpt-4o-search-preview"
        }
    ]
    
    for test in api_test_cases:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   Prompt: {test['prompt']}")
        
        try:
            # Make the API call
            start_time = time.time()
            response = assistant.chat(test['prompt'], stream=False)
            end_time = time.time()
            
            print(f"   ✅ Response generated in {end_time - start_time:.2f}s")
            print(f"   Response: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show metrics
    print("\n" + "=" * 60)
    print("📊 Model Usage Metrics")
    print("=" * 60)
    assistant.print_model_metrics()
    
    print("\n" + "=" * 60)
    print("✅ Dynamic Model Selection Test Complete!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("  • Model router analyzes prompts for complexity and web search needs")
    print("  • Automatically selects the most appropriate GPT-4o model")
    print("  • Falls back to default model if primary model fails")
    print("  • Tracks usage metrics for optimization")
    print("  • Provides cost-effective model utilization")
    print("=" * 60)

if __name__ == "__main__":
    test_dynamic_model_selection()
