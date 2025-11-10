#!/usr/bin/env python3
"""
Demo script showcasing advanced intent awareness and train-of-thought tracking
Demonstrates natural language understanding, entity identification, and thought chain analysis
"""

import os
import sys
import json
import time
from datetime import datetime

# Load environment variables
os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))

try:
    from core_modules.intent_awareness_engine import (
        intent_engine,
        IntentType,
        EntityType,
    )
    from core_modules.train_of_thought_tracker import (
        thought_tracker,
        ThoughtType,
        LinkType,
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the Echoes project root")
    sys.exit(1)


def demo_intent_detection():
    """Demonstrate intent detection capabilities"""
    print("\n" + "=" * 70)
    print("🧠 INTENT AWARENESS ENGINE DEMO")
    print("=" * 70)

    test_messages = [
        "What is machine learning and how does it work?",
        "Create a Python script to analyze data",
        "Compare React vs Angular for web development",
        "I'm getting an error: ImportError cannot find module",
        "Help me understand neural networks",
        "Why is my code running so slow?",
        "Explain the concept of microservices architecture",
        "Can you fix this bug in my application?",
        "Teach me about Docker containers",
        "What are the pros and cons of using TypeScript?",
    ]

    print("\n🎯 Intent Detection Examples:")
    for i, message in enumerate(test_messages, 1):
        print(f'\n  {i}. "{message}"')

        # Detect intent
        intent = intent_engine.detect_intent(message)

        # Extract entities
        entities = intent_engine.extract_entities(message)

        print(f"     → Intent: {intent.type.value.replace('_', ' ').title()}")
        print(f"     → Confidence: {intent.confidence:.2f}")
        if intent.keywords:
            print(f"     → Keywords: {', '.join(intent.keywords)}")
        if intent.parameters:
            print(f"     → Parameters: {intent.parameters}")
        if entities:
            entity_list = [f"{e.text} ({e.type.value})" for e in entities[:3]]
            print(f"     → Entities: {', '.join(entity_list)}")


def demo_entity_extraction():
    """Demonstrate entity extraction capabilities"""
    print("\n" + "=" * 70)
    print("📊 ENTITY IDENTIFICATION DEMO")
    print("=" * 70)

    complex_text = """
    Google and Microsoft are competing in the cloud computing market with AWS and Azure.
    Dr. Smith from MIT published a paper on neural networks using TensorFlow and PyTorch.
    The project, developed in San Francisco, uses React, Node.js, and PostgreSQL.
    Version 2.0.1 was released on December 15, 2023, improving performance by 45%.
    """

    print(f"\nAnalyzing text: {complex_text.strip()}")

    entities = intent_engine.extract_entities(complex_text)

    print(f"\n🔍 Entities Found ({len(entities)} total):")

    # Group by type
    by_type = {}
    for entity in entities:
        if entity.type not in by_type:
            by_type[entity.type] = []
        by_type[entity.type].append(entity)

    for entity_type, type_entities in sorted(by_type.items()):
        print(f"\n  {entity_type.value.title()}:")
        for entity in sorted(type_entities, key=lambda x: x.confidence, reverse=True):
            print(f"    • {entity.text} (confidence: {entity.confidence:.2f})")


def demo_thought_tracking():
    """Demonstrate thought chain tracking"""
    print("\n" + "=" * 70)
    print("🧠 TRAIN OF THOUGHT TRACKING DEMO")
    print("=" * 70)

    # Simulate a problem-solving conversation
    conversation_flow = [
        (
            "I'm having trouble with my Python application",
            ThoughtType.OBSERVATION,
            ["Python", "application"],
        ),
        (
            "The code is throwing an ImportError when I try to import pandas",
            ThoughtType.ANALYSIS,
            ["ImportError", "pandas"],
        ),
        (
            "Maybe pandas is not installed in my virtual environment",
            ThoughtType.HYPOTHESIS,
            ["pandas", "virtual environment"],
        ),
        (
            "Let me check if pandas is installed using pip list",
            ThoughtType.ACTION,
            ["pip", "pandas"],
        ),
        (
            "I can see pandas is not in the installed packages",
            ThoughtType.OBSERVATION,
            ["pandas", "packages"],
        ),
        (
            "I should install pandas using pip install pandas",
            ThoughtType.DECISION,
            ["pip", "pandas"],
        ),
        (
            "After installing pandas, the ImportError should be resolved",
            ThoughtType.CONCLUSION,
            ["pandas", "ImportError"],
        ),
    ]

    print("\n💭 Simulating Problem-Solving Thought Chain:")

    thought_ids = []
    for i, (content, thought_type, entities) in enumerate(conversation_flow, 1):
        print(f"\n  Step {i}: {content}")

        # Add thought
        thought_id = thought_tracker.add_thought(
            thought_id=f"demo_thought_{i}",
            content=content,
            thought_type=thought_type,
            entities=entities,
            parent_thoughts=thought_ids[-1:] if thought_ids else None,
        )
        thought_ids.append(thought_id)

        # Show thought analysis
        thought_meta = thought_tracker.thought_metadata[thought_id]
        print(f"     → Type: {thought_type.value.title()}")
        print(f"     → Importance: {thought_meta['importance']:.2f}")
        print(f"     → Entities: {', '.join(entities)}")


def demo_pattern_detection():
    """Demonstrate pattern detection in thought chains"""
    print("\n" + "=" * 70)
    print("🔍 PATTERN DETECTION DEMO")
    print("=" * 70)

    # Detect patterns in the thought network
    patterns = thought_tracker.detect_patterns()

    print("\n📈 Patterns Detected in Conversation:")

    for pattern_name, pattern_list in patterns.items():
        if pattern_list:
            print(
                f"\n  {pattern_name.replace('_', ' ').title()}: {len(pattern_list)} instances"
            )

            for i, pattern in enumerate(pattern_list[:2], 1):
                print(f"    {i}. {pattern}")
        else:
            print(
                f"\n  {pattern_name.replace('_', ' ').title()}: No instances detected"
            )


def demo_critical_links():
    """Demonstrate critical link identification"""
    print("\n" + "=" * 70)
    print("🔗 CRITICAL CROSS-LINKS DEMO")
    print("=" * 70)

    # Find critical links
    critical_links = thought_tracker.find_critical_links()

    print(f"\n🎯 Critical Links Between Thoughts:")

    if critical_links:
        for i, (from_id, to_id, strength) in enumerate(critical_links[:5], 1):
            from_thought = thought_tracker.thought_metadata.get(from_id, {})
            to_thought = thought_tracker.thought_metadata.get(to_id, {})

            print(f"\n  {i}. Link Strength: {strength:.2f}")

            if from_thought:
                print(
                    f"     From: [{from_thought.get('type', '').title()}] {from_thought.get('content', '')[:60]}..."
                )

            if to_thought:
                print(
                    f"     To: [{to_thought.get('type', '').title()}] {to_thought.get('content', '')[:60]}..."
                )

            # Check if it's a cross-chain link
            from_chain = thought_tracker._get_thought_chain(from_id)
            to_chain = thought_tracker._get_thought_chain(to_id)

            if from_chain != to_chain:
                print(
                    f"     🔗 Cross-chain connection: Chain {from_chain} → Chain {to_chain}"
                )
    else:
        print("  No critical links detected yet.")


def demo_critical_insights():
    """Demonstrate critical insight extraction"""
    print("\n" + "=" * 70)
    print("💡 CRITICAL INSIGHTS DEMO")
    print("=" * 70)

    insights = thought_tracker.get_critical_insights()

    print(f"\n🎯 Critical Insights Extracted:")

    if insights:
        for i, insight in enumerate(insights[:5], 1):
            print(
                f"\n  {i}. {insight.get('insight_type', 'unknown').replace('_', ' ').title()}"
            )
            print(f"     Content: {insight.get('content', '')[:80]}...")
            print(f"     Importance: {insight.get('importance', 0):.2f}")

            if insight.get("connections"):
                print(f"     Connections: {insight['connections']}")

            if insight.get("cross_links"):
                print(f"     Cross-links: {len(insight['cross_links'])}")
    else:
        print("  No critical insights detected yet.")


def demo_conversation_state():
    """Demonstrate conversation state summarization"""
    print("\n" + "=" * 70)
    print("📊 CONVERSATION STATE ANALYSIS DEMO")
    print("=" * 70)

    # Get conversation state from intent engine
    intent_state = intent_engine.summarize_conversation_state()

    print(f"\n🧠 Intent Engine State:")
    print(f"  Total thoughts: {intent_state.get('thought_count', 0)}")
    print(f"  Intent distribution: {intent_state.get('intent_distribution', {})}")
    print(
        f"  Current focus: {intent_state.get('intent_flow', {}).get('current_focus', 'None')}"
    )

    # Get thought network summary
    thought_summary = {
        "total_thoughts": len(thought_tracker.thought_metadata),
        "total_chains": len(thought_tracker.chains),
        "total_links": thought_tracker.thought_network.number_of_edges(),
        "active_chains": len(thought_tracker.active_chains),
    }

    print(f"\n🧠 Thought Network State:")
    for key, value in thought_summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


def demo_export_functionality():
    """Demonstrate export functionality"""
    print("\n" + "=" * 70)
    print("💾 THOUGHT NETWORK EXPORT DEMO")
    print("=" * 70)

    # Export the thought network
    export_data = thought_tracker.export_thought_network()

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"demo_thought_network_{timestamp}.json"

    try:
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\n✅ Thought network exported to: {filename}")
        print(f"   File size: {os.path.getsize(filename):,} bytes")
        print(f"   Thoughts: {len(export_data['thoughts'])}")
        print(f"   Links: {len(export_data['links'])}")
        print(f"   Chains: {len(export_data['chains'])}")
        print(f"   Patterns: {len(export_data['patterns'])}")
        print(f"   Insights: {len(export_data['critical_insights'])}")

        # Show a sample of the exported data
        print(f"\n📄 Sample Export Structure:")
        print(f"   {{")
        print(f"     \"thoughts\": {len(export_data['thoughts'])} items,")
        print(f"     \"links\": {len(export_data['links'])} items,")
        print(f"     \"chains\": {len(export_data['chains'])} items,")
        print(f"     \"patterns\": {list(export_data['patterns'].keys())},")
        print(
            f"     \"critical_insights\": {len(export_data['critical_insights'])} items"
        )
        print(f"   }}")

    except Exception as e:
        print(f"❌ Export failed: {e}")


def demo_advanced_features():
    """Demonstrate advanced features integration"""
    print("\n" + "=" * 70)
    print("🚀 ADVANCED FEATURES INTEGRATION DEMO")
    print("=" * 70)

    # Complex scenario: Multi-domain problem solving
    scenario = """
    I'm working on a machine learning project at Google to predict customer churn.
    The neural network model using TensorFlow is not converging properly.
    I think the issue might be with the data preprocessing or the learning rate.
    Should I try a different architecture like XGBoost instead?
    """

    print(f"\n🎯 Complex Scenario Analysis:")
    print(f"   {scenario.strip()}")

    # Comprehensive analysis
    intent = intent_engine.detect_intent(scenario)
    entities = intent_engine.extract_entities(scenario)

    print(f"\n🧠 Intent Analysis:")
    print(f"   Primary Intent: {intent.type.value.replace('_', ' ').title()}")
    print(f"   Confidence: {intent.confidence:.2f}")

    print(f"\n📊 Entity Analysis:")
    entity_groups = {}
    for entity in entities:
        if entity.type not in entity_groups:
            entity_groups[entity.type] = []
        entity_groups[entity.type].append(entity.text)

    for entity_type, entity_list in entity_groups.items():
        print(f"   {entity_type.value.title()}: {', '.join(entity_list)}")

    # Create thought for this complex scenario
    thought_id = thought_tracker.add_thought(
        thought_id=f"complex_scenario_{int(time.time())}",
        content=scenario,
        thought_type=ThoughtType.PROBLEM_SOLVING,
        entities=[e.text for e in entities],
    )

    # Get thought importance
    thought_meta = thought_tracker.thought_metadata[thought_id]

    print(f"\n💭 Thought Analysis:")
    print(f"   Thought Type: {ThoughtType.PROBLEM_SOLVING.value.title()}")
    print(f"   Importance Score: {thought_meta['importance']:.2f}")
    print(f"   Entity Count: {len(thought_meta['entities'])}")
    print(f"   Word Count: {thought_meta['metadata']['word_count']}")

    # Generate insights
    insights = thought_tracker.get_critical_insights()
    scenario_insights = [
        i
        for i in insights
        if thought_id in [i.get("thought_id", ""), i.get("thought_id", "")]
    ]

    if scenario_insights:
        print(f"\n💡 Generated Insights:")
        for insight in scenario_insights[:2]:
            print(
                f"   • {insight.get('insight_type', 'unknown')}: High importance thought with multiple entities"
            )


def main():
    """Run all demos"""
    print("\n✨ Welcome to the Advanced Intent Awareness & Thought Tracking Demo!")
    print("This showcases natural language understanding, entity identification,")
    print("and intelligent thought chain analysis capabilities.")

    # Run all demos
    demo_intent_detection()
    demo_entity_extraction()
    demo_thought_tracking()
    demo_pattern_detection()
    demo_critical_links()
    demo_critical_insights()
    demo_conversation_state()
    demo_export_functionality()
    demo_advanced_features()

    print("\n" + "=" * 70)
    print("🎉 Demo Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Advanced intent detection with 12 intent types")
    print("  ✅ Comprehensive entity identification across 13 categories")
    print("  ✅ Train-of-thought tracking with 9 thought types")
    print(
        "  ✅ Automatic pattern detection (problem-solution, hypothesis testing, etc.)"
    )
    print("  ✅ Critical cross-link identification between thought chains")
    print("  ✅ Intelligent insight extraction from conversation flow")
    print("  ✅ Full conversation state analysis and export")
    print("  ✅ Multi-domain integration and complex scenario handling")

    print("\nTry the interactive mode with:")
    print("  python assistant_v2_core.py")
    print("  Then try commands like:")
    print("    intent <your text>      - Analyze intent and entities")
    print("    thoughts                - Show thought chain analysis")
    print("    links                   - Show critical cross-links")
    print("    export                  - Export thought network")


if __name__ == "__main__":
    main()
