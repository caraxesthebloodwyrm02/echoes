#!/usr/bin/env python3
"""
Context-Aware API Call Demonstration
====================================

This script demonstrates the full capabilities of the Context-Aware AI Agent
that we've built for the Echoes platform. It showcases:

1. Multi-step reasoning with tool chaining
2. Codebase awareness through file search and reading
3. Context integration from user trajectory
4. Intelligent intent recognition and error recovery

The agent can answer complex questions about the codebase by:
- Searching for relevant files (fuzzy matching by name or content)
- Reading file contents with security boundaries
- Synthesizing information across multiple sources
- Maintaining context throughout the conversation

Usage:
    python examples/run_context_aware_call.py [--query "custom query"]

Example Queries:
    - "Explain how the GuardrailMiddleware enforces security protocols"
    - "What are the key features of the context-aware API system?"
    - "How does the documentation-driven security work?"
    - "Show me the integration between Glimpse and the security middleware"
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.context_aware_api import ContextAwareAPICall
from core.realtime_preview import create_glimpse


def simulate_realistic_trajectory(glimpse_system) -> dict[str, Any]:
    """
    Simulate a realistic development trajectory that provides meaningful context
    for the AI agent to work with.
    """
    print("📝 Simulating realistic development trajectory...")

    # Simulate working on security middleware
    glimpse_system.process_input(
        "insert",
        position=0,
        text="""# Working on GuardrailMiddleware integration
class SecurityProtocolParser:
    def __init__(self, docs_path: str):
        self.docs_path = docs_path

    def parse_protocols(self) -> List[Dict]:
        # Parse security protocols from markdown docs
        return self._extract_security_rules()""",
    )

    # Simulate editing and refining
    glimpse_system.process_input(
        "replace",
        start=50,
        end=80,
        text="Enhanced security protocol parser with validation",
    )

    # Simulate adding documentation
    glimpse_system.process_input(
        "insert",
        position=200,
        text="""

    def validate_request(self, request_data: Dict) -> bool:
        \"\"\"Validate incoming request against security protocols\"\"\"
        # Implementation for request validation
        return self._check_security_constraints(request_data)""",
    )

    trajectory_summary = {
        "session_duration": "45 minutes",
        "files_modified": ["middleware.py", "security_parser.py"],
        "features_worked_on": ["security validation", "protocol parsing"],
        "current_focus": "GuardrailMiddleware integration",
        "recent_changes": [
            "Added security protocol parser",
            "Implemented request validation",
            "Enhanced documentation parsing",
        ],
    }

    print(
        f"✅ Trajectory simulation complete. Context: {len(str(trajectory_summary))} chars"
    )
    return trajectory_summary


def run_comprehensive_demo(context_api: ContextAwareAPICall) -> list[dict[str, Any]]:
    """
    Run a comprehensive demonstration of the context-aware API capabilities
    with multiple queries that showcase different aspects of the system.
    """

    demo_queries = [
        {
            "title": "Security Architecture Analysis",
            "query": """I'm working on understanding the security architecture of this project.
            Can you explain how the GuardrailMiddleware class works, what security protocols it enforces,
            and how it integrates with the documentation-driven security approach?
            Please provide specific details about its implementation and key methods.""",
            "expected_capabilities": [
                "file search",
                "content analysis",
                "architectural understanding",
            ],
        },
        {
            "title": "Context-Aware System Analysis",
            "query": """I need to understand the context-aware API system that was recently implemented.
            How does the ContextAwareAPICall class work? What tools does it have available,
            and how does it chain multiple operations together? Show me the key implementation details.""",
            "expected_capabilities": [
                "self-analysis",
                "multi-step reasoning",
                "tool introspection",
            ],
        },
        {
            "title": "Integration and Workflow Analysis",
            "query": """How do the Glimpse system, GuardrailMiddleware, and ContextAwareAPICall work together?
            What's the overall workflow when a user makes a request? Please trace through the complete
            integration and explain how trajectory context is used.""",
            "expected_capabilities": [
                "system integration analysis",
                "workflow tracing",
                "context synthesis",
            ],
        },
    ]

    results = []

    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{'='*80}")
        print(f"🔍 DEMO {i}/3: {demo['title']}")
        print(f"{'='*80}")
        print(f"📋 Query: {demo['query'][:100]}...")
        print(f"🎯 Expected Capabilities: {', '.join(demo['expected_capabilities'])}")
        print(f"{'='*80}")

        start_time = time.time()

        try:
            result = context_api.run(demo["query"])
            execution_time = time.time() - start_time

            results.append(
                {
                    "demo_number": i,
                    "title": demo["title"],
                    "query": demo["query"],
                    "result": result,
                    "execution_time": execution_time,
                    "status": "success",
                }
            )

            print(f"\n✅ Demo {i} completed successfully in {execution_time:.2f}s")

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"\n❌ Demo {i} failed after {execution_time:.2f}s: {str(e)}")

            results.append(
                {
                    "demo_number": i,
                    "title": demo["title"],
                    "query": demo["query"],
                    "error": str(e),
                    "execution_time": execution_time,
                    "status": "failed",
                }
            )

        # Brief pause between demos
        if i < len(demo_queries):
            print("\n⏸️  Pausing 2 seconds before next demo...")
            time.sleep(2)

    return results


def generate_performance_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a comprehensive performance and capability report."""

    successful_demos = [r for r in results if r["status"] == "success"]
    failed_demos = [r for r in results if r["status"] == "failed"]

    total_time = sum(r["execution_time"] for r in results)
    avg_time = total_time / len(results) if results else 0

    report = {
        "summary": {
            "total_demos": len(results),
            "successful": len(successful_demos),
            "failed": len(failed_demos),
            "success_rate": len(successful_demos) / len(results) * 100
            if results
            else 0,
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
        },
        "capabilities_demonstrated": [
            "Multi-step reasoning with tool chaining",
            "Fuzzy file search (by name and content)",
            "Secure file reading with boundary checks",
            "Intent recognition and error recovery",
            "Context integration from user trajectory",
            "Self-analysis and introspection",
            "System integration analysis",
        ],
        "performance_metrics": {
            "fastest_query": min(results, key=lambda x: x["execution_time"])[
                "execution_time"
            ]
            if results
            else 0,
            "slowest_query": max(results, key=lambda x: x["execution_time"])[
                "execution_time"
            ]
            if results
            else 0,
            "queries_per_minute": 60 / avg_time if avg_time > 0 else 0,
        },
        "detailed_results": results,
    }

    return report


def print_final_report(report: dict[str, Any]):
    """Print a comprehensive final report of the demonstration."""

    print(f"\n{'='*80}")
    print("📊 CONTEXT-AWARE API DEMONSTRATION REPORT")
    print(f"{'='*80}")

    summary = report["summary"]
    print(
        f"🎯 Success Rate: {summary['success_rate']:.1f}% ({summary['successful']}/{summary['total_demos']} demos)"
    )
    print(f"⏱️  Total Time: {summary['total_execution_time']:.2f}s")
    print(f"📈 Average Time: {summary['average_execution_time']:.2f}s per query")

    perf = report["performance_metrics"]
    print(f"🚀 Performance: {perf['queries_per_minute']:.1f} queries/minute")
    print(
        f"⚡ Fastest: {perf['fastest_query']:.2f}s | 🐌 Slowest: {perf['slowest_query']:.2f}s"
    )

    print("\n✨ Capabilities Demonstrated:")
    for i, capability in enumerate(report["capabilities_demonstrated"], 1):
        print(f"   {i}. {capability}")

    print("\n📋 Detailed Results:")
    for result in report["detailed_results"]:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(
            f"   {status_icon} Demo {result['demo_number']}: {result['title']} ({result['execution_time']:.2f}s)"
        )

    print(f"\n{'='*80}")
    print("🎉 DEMONSTRATION COMPLETE - Context-Aware AI Agent is fully operational!")
    print(f"{'='*80}")


def main():
    """
    Main demonstration function that showcases the complete Context-Aware API system.
    """
    parser = argparse.ArgumentParser(description="Context-Aware API Demonstration")
    parser.add_argument(
        "--query",
        type=str,
        help="Custom query to run instead of the full demonstration",
    )
    parser.add_argument(
        "--quick", action="store_true", help="Run a quick single-query demo"
    )

    args = parser.parse_args()

    print("🚀 CONTEXT-AWARE API DEMONSTRATION")
    print("=" * 50)
    print("Initializing Echoes Platform Context-Aware AI Agent...")
    print("This demonstration showcases multi-step reasoning, codebase awareness,")
    print("and intelligent tool chaining capabilities.\n")

    # Initialize the Glimpse system with realistic settings
    print("🔧 Initializing Glimpse System...")
    glimpse_system = create_glimpse(enable_security=True, enable_guardrails=True)
    glimpse_system.start()

    # Simulate realistic development trajectory
    simulate_realistic_trajectory(glimpse_system)

    # Initialize the Context-Aware API handler
    print("\n🤖 Initializing Context-Aware API Handler...")
    context_api = ContextAwareAPICall(glimpse_system)

    if args.query:
        # Run custom query
        print(f"\n🔍 Running custom query: {args.query}")
        start_time = time.time()
        context_api.run(args.query)
        execution_time = time.time() - start_time
        print(f"\n✅ Query completed in {execution_time:.2f}s")

    elif args.quick:
        # Run quick demo
        print("\n🔍 Running quick demonstration...")
        quick_query = """Explain the GuardrailMiddleware class and how it enforces security protocols
        based on documentation. Include key implementation details."""

        start_time = time.time()
        context_api.run(quick_query)
        execution_time = time.time() - start_time
        print(f"\n✅ Quick demo completed in {execution_time:.2f}s")

    else:
        # Run comprehensive demonstration
        print("\n🎭 Running comprehensive demonstration suite...")
        results = run_comprehensive_demo(context_api)

        # Generate and display performance report
        report = generate_performance_report(results)
        print_final_report(report)


if __name__ == "__main__":
    main()
