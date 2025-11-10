#!/usr/bin/env python3
"""
Agentic Capabilities Demonstration

Shows how EchoesAssistantV2 can now:
- Search the web for real-time information
- Read and write files
- Use OpenAI function calling for complex tasks
- Combine multiple tools for sophisticated workflows
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from assistant_v2_core import EchoesAssistantV2


def demo_agentic_capabilities():
    """Demonstrate the enhanced agentic capabilities."""

    print("=" * 80)
    print("🤖 EchoesAssistantV2 - Agentic Capabilities Demo")
    print("=" * 80)

    # Initialize assistant with all capabilities
    print("\n📦 Initializing EchoesAssistantV2 with full agentic capabilities...")
    assistant = EchoesAssistantV2(
        enable_tools=True,
        enable_rag=True,
        enable_status=True,
        session_id="agentic_demo",
    )

    print("✅ Assistant ready!")
    print(f"   Total tools available: {len(assistant.list_tools())}")

    # Show all available tools
    print("\n🔧 Available Tools:")
    all_tools = assistant.list_tools()
    categories = {
        "Filesystem": [
            "read_file",
            "write_file",
            "list_directory",
            "search_files",
            "create_directory",
            "get_file_info",
        ],
        "Web Search": ["web_search", "get_web_page_content"],
        "General": ["calculator", "text_analyzer"],
    }

    for category, tools in categories.items():
        print(f"\n  📂 {category}:")
        for tool in tools:
            if tool in all_tools:
                print(f"    ✅ {tool}")
            else:
                print(f"    ❌ {tool}")

    # Demo scenarios
    demo_scenarios = [
        {
            "title": "🔍 Research and Document Creation",
            "description": "Search web for AI trends and create a summary document",
            "prompt": "Search for the latest trends in AI development in 2025 and create a markdown file called 'ai_trends_2025.md' with a summary of what you find.",
        },
        {
            "title": "📊 Data Analysis and Reporting",
            "description": "Analyze project files and generate a report",
            "prompt": "List all Python files in the current directory, analyze their content to identify the main components of this project, and create a report file called 'project_analysis.md'.",
        },
        {
            "title": "🌐 Real-time Information Gathering",
            "description": "Fetch current information from the web",
            "prompt": "Search for information about OpenAI's latest API updates and summarize the key features for developers.",
        },
        {
            "title": "📝 Knowledge Management",
            "description": "Add information to knowledge base and retrieve it",
            "prompt": "Add to your knowledge that EchoesAssistantV2 now has web search capabilities, then search your knowledge for information about web search features.",
        },
    ]

    print("\n" + "=" * 80)
    print("🚀 Interactive Demo Scenarios")
    print("=" * 80)

    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{scenario['title']}")
        print(f"   {scenario['description']}")
        print(f"   💬 Prompt: {scenario['prompt']}")

        # Execute the scenario
        print("   🤖 Executing...")
        try:
            response = assistant.chat(scenario["prompt"], stream=False)

            # Show truncated response
            if len(response) > 200:
                print(f"   ✅ Response: {response[:200]}...")
            else:
                print(f"   ✅ Response: {response}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("-" * 60)

    # Show tool schemas
    print("\n" + "=" * 80)
    print("📋 Tool Schemas (OpenAI Function Calling)")
    print("=" * 80)

    if assistant.tool_registry:
        # Show web search tool schema
        web_search = assistant.tool_registry.get("web_search")
        if web_search:
            schema = web_search.to_openai_schema()
            func = schema["function"]
            print(f"\n🔍 {func['name']}")
            print(f"   Description: {func['description']}")
            print(f"   Parameters: {list(func['parameters']['properties'].keys())}")

        # Show filesystem tool schema
        read_file = assistant.tool_registry.get("read_file")
        if read_file:
            schema = read_file.to_openai_schema()
            func = schema["function"]
            print(f"\n📁 {func['name']}")
            print(f"   Description: {func['description']}")
            print(f"   Parameters: {list(func['parameters']['properties'].keys())}")

    print("\n" + "=" * 80)
    print("✅ Agentic Capabilities Summary")
    print("=" * 80)
    print("The EchoesAssistantV2 now has true agentic capabilities:")
    print("\n🌐 Web Access:")
    print("  • Real-time web search via multiple providers")
    print("  • Web page content extraction")
    print("  • No API key required for basic search (DuckDuckGo)")
    print("  • Optional premium providers (Brave, Google)")

    print("\n📁 Filesystem Interaction:")
    print("  • Read/write files with safety checks")
    print("  • Directory navigation and listing")
    print("  • File search by name or content")
    print("  • Metadata extraction")

    print("\n🧠 Knowledge Management:")
    print("  • OpenAI embeddings for semantic search")
    print("  • Document storage and retrieval")
    print("  • Context-aware responses")

    print("\n🔧 Tool Integration:")
    print("  • OpenAI function calling compatible")
    print("  • Multi-step tool execution")
    print("  • Error handling and validation")
    print("  • Extensible architecture")

    print("\n🎯 Use Cases:")
    print("  • Research assistants")
    print("  • Document analysis")
    print("  • Code exploration")
    print("  • Real-time information gathering")
    print("  • Automated reporting")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    demo_agentic_capabilities()
