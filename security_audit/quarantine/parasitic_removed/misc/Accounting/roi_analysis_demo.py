#!/usr/bin/env python3
"""
ROI Analysis Tool Demo for EchoesAssistantV2

Demonstrates the complete ROI analysis generation capability including:
- Tool registration and execution
- Multi-format file generation (YAML, CSV, spreadsheet, report)
- Automatic file organization
- Knowledge base integration
- Action executor integration
"""

from pathlib import Path

from assistant_v2_core import EchoesAssistantV2


def demo_roi_analysis():
    """Complete ROI analysis demo."""

    print("🎯 EchoesAssistantV2 - ROI Analysis Tool Demo")
    print("=" * 60)

    # Initialize assistant
    print("\n1. Initializing EchoesAssistantV2...")
    assistant = EchoesAssistantV2(
        enable_tools=True, enable_rag=True, enable_status=True
    )
    print("✓ Assistant initialized with tools and RAG enabled")

    # Demo data
    roi_params = {
        "business_type": "financial",
        "analysis_data": {
            "monthly_investment": 12000,
            "monthly_savings": 71822,
            "team_size": 5,
        },
        "stakeholder_info": {
            "institution_name": "Demo Bank Corp",
            "email_to": ["cfo@demobank.com", "cto@demobank.com", "cco@demobank.com"],
        },
        "output_formats": ["yaml", "csv", "spreadsheet", "report"],
        "customization_level": "comprehensive",
    }

    print("\n2. Executing ROI analysis via action executor...")
    print(f"   Business Type: {roi_params['business_type']}")
    print(f"   Institution: {roi_params['stakeholder_info']['institution_name']}")
    print(
        f"   Monthly Investment: ${roi_params['analysis_data']['monthly_investment']:,}"
    )
    print(f"   Monthly Savings: ${roi_params['analysis_data']['monthly_savings']:,}")

    # Execute ROI analysis action
    result = assistant.execute_action(
        action_type="roi", action_name="generate_roi_package", **roi_params
    )

    if result["success"]:
        print("✓ ROI analysis completed successfully!")
        print(f"   Analysis ID: {result['result'].get('analysis_id', 'N/A')}")
        print(f"   Generated {result['result'].get('file_count', 0)} file types")

        # Show file organization
        file_org = result["result"].get("file_organization", {})
        if file_org.get("success"):
            print("\n📁 Files organized in:")
            print(f"   Base directory: {file_org.get('base_directory')}")
            print(f"   Institution directory: {file_org.get('institution_directory')}")
            print(f"   Total files: {file_org.get('total_files')}")

            organized_files = file_org.get("organized_files", {})
            print("\n📄 Generated files:")
            for file_type, path in organized_files.items():
                if file_type != "metadata":
                    print(f"   • {file_type}: {Path(path).name}")

        # Show ROI metrics
        roi_metrics = result["result"].get("roi_metrics", {})
        print("\n📊 ROI Metrics:")
        print(f"   Payback Period: {roi_metrics.get('payback_days', 0):.0f} days")
        print(f"   ROI: {roi_metrics.get('roi_percentage', 0):.0f}%")
        print(
            f"   Annual Net Benefit: ${roi_metrics.get('annual_net_benefit', 0):,.0f}"
        )

        print("\n3. Testing knowledge base integration...")
        # Test knowledge search
        roi_analyses = assistant.search_roi_analyses(
            institution="Demo Bank Corp", limit=5  # Use exact name from stored content
        )
        print(f"✓ Found {len(roi_analyses)} ROI analyses in knowledge base")

        # Show ROI summary
        roi_summary = assistant.get_roi_summary()
        print("\n📈 ROI Knowledge Summary:")
        print(f"   Total analyses: {roi_summary.get('total_analyses', 0)}")
        print(
            f"   Institutions analyzed: {len(roi_summary.get('institutions_analyzed', []))}"
        )
        print(f"   Success rate: {roi_summary.get('success_rate', 0):.1f}%")
        print("\n4. Testing filesystem integration...")
        # List organized directory
        list_result = assistant.list_directory("roi_analysis", recursive=True)
        if list_result["success"]:
            print(
                f"✓ ROI directory contains {list_result['total_files']} files in {list_result['total_dirs']} directories"
            )
        else:
            print(f"⚠ Could not list directory: {list_result.get('error')}")

        print("\n5. Testing tool execution via chat interface...")
        # Test direct tool call via chat
        chat_message = "Please generate an ROI analysis for a healthcare provider with $15,000 monthly investment, $85,000 monthly savings, and send results to admin@healthcare.com"
        print(f"   Chat input: {chat_message[:80]}...")

        chat_response = assistant.chat(message=chat_message, show_status=False)

        if "Error" not in chat_response:
            print("✓ Chat-based ROI generation successful")
        else:
            print(f"⚠ Chat execution had issues: {chat_response[:100]}...")

    else:
        print(f"✗ ROI analysis failed: {result.get('error', 'Unknown error')}")

    # Show action history
    print("\n6. Action history summary:")
    action_summary = assistant.get_action_summary()
    print(f"   Total actions: {action_summary['total_actions']}")
    print(f"   Success rate: {action_summary['success_rate']:.1f}%")
    print(f"   Avg duration: {action_summary['avg_duration_ms']:.1f}ms")
    # Final stats
    stats = assistant.get_stats()
    print("\n7. Final assistant statistics:")
    print(f"   Session: {stats.get('session_id', 'N/A')[:8]}...")

    # Fix stats display to use correct keys
    tool_stats = stats.get("tool_stats", {})
    knowledge_stats = stats.get("knowledge", {})
    print(f"   Tools available: {tool_stats.get('total_tools', 0)}")
    print(f"   Knowledge entries: {knowledge_stats.get('total_entries', 0)}")

    print("\n🎉 ROI Analysis Tool Demo Complete!")
    print("The assistant can now generate comprehensive ROI analysis packages")
    print("including stakeholder emails, spreadsheets, and executive reports.")
    print("=" * 60)


if __name__ == "__main__":
    demo_roi_analysis()
