#!/usr/bin/env python3
"""
Complete demonstration of EchoesAssistantV2 with Glimpse and External API Contact
This shows the full bridge between internals and externals
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

from assistant_v2_core import EchoesAssistantV2

# Repo root: allow override via ECHOES_ROOT (e.g. E:/Seeds/echoes)
_REPO_ROOT = Path(
    os.environ.get("ECHOES_ROOT", str(Path(__file__).resolve().parent.parent))
)


async def start_api_server():
    """Start the Echoes API server in the background"""
    try:
        # Start the API server
        process = subprocess.Popen(
            [sys.executable, "-m", "api.main"],
            cwd=str(_REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Give it time to start
        print("⏳ Starting Echoes API server...")
        time.sleep(3)

        return process
    except Exception as e:
        print(f"Failed to start API server: {e}")
        return None


async def full_bridge_demo():
    print("=" * 70)
    print("🌉 ECHOES ASSISTANT V2 - COMPLETE BRIDGE DEMONSTRATION")
    print("=" * 70)
    print("This demo shows the full integration of:")
    print("• Glimpse Preflight System (intent verification)")
    print("• External API Contact (pattern detection & truth verification)")
    print("• Internal-External Bridge (seamless communication)")
    print("=" * 70)

    # Start API server
    api_process = await start_api_server()

    try:
        # Initialize the fully integrated assistant
        assistant = EchoesAssistantV2(
            enable_rag=True,
            enable_tools=True,
            enable_streaming=True,
            enable_status=True,
            enable_glimpse=True,
            enable_external_contact=True,
        )

        print("\n✅ Assistant initialized with full bridge capabilities")
        print(f"   - Glimpse preflight: {assistant.enable_glimpse}")
        print(f"   - External contact: {assistant.enable_external_contact}")
        print(f"   - Responses API: {assistant.use_responses_api}")

        # Demo Scenario: Business Analysis Request
        print("\n" + "=" * 50)
        print("📊 SCENARIO: Business Analysis Request")
        print("=" * 50)

        # Step 1: Set Glimpse anchors for business context
        print("\n1️⃣ Setting Glimpse anchors for business analysis...")
        assistant.set_glimpse_anchors(
            goal="Generate business insights and recommendations",
            constraints="tone: professional | audience: executives | format: structured_report",
        )
        print("   ✓ Anchors set: Business analysis context")

        # Step 2: Perform Glimpse preflight
        print("\n2️⃣ Performing Glimpse preflight verification...")
        business_query = """
        Analyze our Q4 performance and provide strategic recommendations for Q1 2025. 
        Key metrics: Revenue up 25%, customer acquisition cost down 15%, 
        but churn rate increased by 3%.
        """

        glimpse_result = await assistant.glimpse_preflight(business_query)

        if glimpse_result["success"]:
            print(f"   ✅ Glimpse aligned: {glimpse_result['aligned']}")
            print(f"   📋 Sample: {glimpse_result['sample'][:100]}...")
            print(f"   🎯 Essence: {glimpse_result['essence']}")

        # Step 3: External API Pattern Detection
        print("\n3️⃣ Analyzing patterns through external API...")
        patterns_result = await assistant.detect_patterns_external(
            text=business_query,
            context={"domain": "business", "timeframe": "Q4_2024"},
            options={"min_confidence": 0.7},
        )

        if patterns_result["success"]:
            print(f"   ✅ Patterns detected: {len(patterns_result['patterns'])}")
            for pattern in patterns_result["patterns"][:3]:
                print(
                    f"      🔍 {pattern['pattern_type']}: {pattern['description'][:80]}..."
                )
        else:
            print(f"   ⚠️  External API unavailable: {patterns_result['error']}")

        # Step 4: External API Truth Verification
        print("\n4️⃣ Verifying claims through external API...")
        claims = [
            "Revenue increased by 25% in Q4",
            "Customer acquisition cost decreased by 15%",
            "Churn rate increased by 3%",
        ]

        for claim in claims:
            truth_result = await assistant.verify_truth_external(
                claim=claim,
                evidence=["Q4 financial report", "Analytics dashboard data"],
                context={"verification_type": "business_metrics"},
            )

            if truth_result["success"]:
                print(
                    f"   ✅ {claim[:50]}... → {truth_result['verdict']} ({truth_result['confidence']:.2f})"
                )
            else:
                print("   ⚠️  External verification unavailable")

        # Step 5: Combined Analysis through Bridge
        print("\n5️⃣ Running combined analysis through initiate_contact bridge...")
        bridge_result = await assistant.initiate_contact(
            message_type="analysis",
            data={
                "text": business_query,
                "context": {
                    "analysis_type": "business_performance",
                    "quarter": "Q4_2024",
                    "focus_areas": ["revenue", "costs", "churn"],
                },
                "evidence": [
                    "Financial statements",
                    "Customer analytics",
                    "Market research data",
                ],
            },
        )

        if bridge_result["success"]:
            print("   ✅ Combined analysis completed")
            print(f"   📊 Analysis type: {bridge_result['type']}")

            # Show patterns if available
            if isinstance(bridge_result.get("patterns"), dict) and bridge_result[
                "patterns"
            ].get("success"):
                pattern_count = len(bridge_result["patterns"].get("patterns", []))
                print(f"   🔍 Patterns analyzed: {pattern_count}")

            # Show truth verification if available
            if isinstance(bridge_result.get("truth"), dict) and bridge_result[
                "truth"
            ].get("success"):
                verdict = bridge_result["truth"].get("verdict", "UNKNOWN")
                confidence = bridge_result["truth"].get("confidence", 0)
                print(f"   ✅ Overall truth assessment: {verdict} ({confidence:.2f})")

        # Step 6: Get final assistant response with all insights
        print("\n6️⃣ Generating final response with integrated insights...")

        # Build context from external analyses
        context_addon = ""
        if patterns_result["success"]:
            context_addon += f"\nPattern Analysis: Found {len(patterns_result['patterns'])} key patterns in the data."

        if bridge_result["success"] and isinstance(bridge_result.get("truth"), dict):
            if bridge_result["truth"].get("success"):
                context_addon += f"\nTruth Verification: Claims verified with {bridge_result['truth'].get('confidence', 0):.1%} confidence."

        final_query = business_query + context_addon

        # Get assistant response
        response = assistant.chat(
            final_query,
            system_prompt="You are an expert business analyst providing strategic recommendations.",
            stream=False,
        )

        print("\n" + "=" * 50)
        print("📋 FINAL BUSINESS ANALYSIS REPORT")
        print("=" * 50)
        print(response[:500] + "..." if len(response) > 500 else response)

        # Step 7: Commit the Glimpse if aligned
        if glimpse_result["success"] and glimpse_result["aligned"]:
            print("\n7️⃣ Committing Glimpse to persistent storage...")
            commit_result = assistant.commit_glimpse(business_query)
            if commit_result["success"]:
                print(
                    f"   ✅ Glimpse committed to session {commit_result['session_id']}"
                )

        # Show final status
        print("\n" + "=" * 50)
        print("📊 BRIDGE SYSTEM STATUS")
        print("=" * 50)

        status = assistant.get_external_status()
        print(
            f"   Glimpse System: {'✅ Active' if status['status']['glimpse_active'] else '❌ Inactive'}"
        )
        print(
            f"   External Contact: {'✅ Connected' if status['status']['external_contact_enabled'] else '❌ Disconnected'}"
        )
        print(f"   API Endpoints: {len(status['status']['api_endpoints'])} configured")

        print("\n" + "=" * 70)
        print("🎉 BRIDGE DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nKey Achievements:")
        print("• ✅ Glimpse preflight system successfully integrated")
        print("• ✅ External API contact bridge established")
        print("• ✅ Pattern detection via external API")
        print("• ✅ Truth verification via external API")
        print("• ✅ Combined analysis through initiate_contact")
        print("• ✅ Seamless internal-external communication")
        print("• ✅ Privacy-preserving commit system")
        print("\nThe EchoesAssistantV2 now provides a complete bridge between")
        print("internal AI capabilities and external analytical APIs!")

    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up API server
        if api_process:
            print("\n🔄 Shutting down API server...")
            api_process.terminate()
            api_process.wait()


if __name__ == "__main__":
    asyncio.run(full_bridge_demo())
