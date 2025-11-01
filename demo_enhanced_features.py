#!/usr/bin/env python3
"""
Demo script showcasing the enhanced Echoes Assistant with:
- Dynamic error handling and automated fixes
- Personality engine with enthusiasm, curiosity, and mood adaptation
- Cross-reference system for intelligent context understanding
- Values-driven responses
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from assistant_v2_core import EchoesAssistantV2
    from core_modules.personality_engine import personality_engine, Mood, PersonalityTrait
    from core_modules.dynamic_error_handler import error_handler
    from core_modules.cross_reference_system import cross_reference_system
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running this from the Echoes project root")
    sys.exit(1)

def demo_personality():
    """Demonstrate personality engine capabilities"""
    print("\n" + "="*60)
    print("🎭 PERSONALITY ENGINE DEMO")
    print("="*60)
    
    # Show initial personality state
    print("\n📊 Initial Personality State:")
    stats = personality_engine.get_personality_summary()
    print(f"  Current Mood: {stats['current_mood']}")
    print(f"  Top Traits: {stats['dominant_traits'][:2]}")
    
    # Simulate user interactions and show adaptation
    interactions = [
        "I'm so excited about this project! It's amazing!",
        "Why does the code work this way? I'm curious about the design.",
        "I'm feeling stuck and need help with this difficult problem.",
        "Let's have some fun and play with some creative ideas!",
        "I need to focus and get serious work done now.",
    ]
    
    print("\n🔄 Personality Adaptation:")
    for i, message in enumerate(interactions, 1):
        print(f"\n  Interaction {i}: {message}")
        personality_engine.update_from_interaction(message)
        stats = personality_engine.get_personality_summary()
        print(f"    → Mood shifted to: {stats['current_mood']}")
        
        # Generate a response prefix
        prefix = personality_engine.generate_response_prefix("response")
        print(f"    → Response style: {prefix}")

def demo_error_handling():
    """Demonstrate dynamic error handling"""
    print("\n" + "="*60)
    print("🔧 DYNAMIC ERROR HANDLING DEMO")
    print("="*60)
    
    # Simulate various errors and show fixes
    test_errors = [
        ImportError("cannot import name 'MissingModule'"),
        AttributeError("'ToolRegistry' object has no attribute 'get_openai_schemas'"),
        TypeError("SimpleRAGSystem.search() got an unexpected keyword argument 'top_k'"),
        ValueError("No module named 'nonexistent_package'"),
    ]
    
    print("\n🚨 Error Detection and Auto-Fixes:")
    for i, error in enumerate(test_errors, 1):
        print(f"\n  Test Error {i}: {type(error).__name__}: {error}")
        
        # Handle the error
        result = error_handler.handle_error(error, {"test": True})
        
        print(f"    → Category: {result['analysis']['category']}")
        print(f"    → Severity: {result['analysis']['severity']}")
        
        if result.get("fix_attempted"):
            fix = result.get("fix_result", {})
            if fix:
                print(f"    🔧 Auto-fix available: {fix.get('suggestion', 'N/A')}")
                if fix.get("code_fix"):
                    print(f"    💡 Code suggestion: {fix.get('code_fix')}")
    
    # Show error statistics
    stats = error_handler.get_fix_statistics()
    print(f"\n📈 Error Handler Statistics:")
    print(f"  Total Errors: {stats['total_errors']}")
    print(f"  Auto-fix Success Rate: {stats['auto_fix_success_rate']:.1%}")

def demo_cross_references():
    """Demonstrate cross-reference system"""
    print("\n" + "="*60)
    print("🔗 CROSS-REFERENCE SYSTEM DEMO")
    print("="*60)
    
    # Test different topics
    topics = [
        "machine learning algorithms",
        "creative writing techniques",
        "business strategy development",
        "philosophy of mind",
    ]
    
    print("\n🧠 Context Analysis and Cross-References:")
    for topic in topics:
        print(f"\n  Topic: '{topic}'")
        
        # Analyze context
        context = cross_reference_system.analyze_context(f"Tell me about {topic}")
        print(f"    → Domains: {', '.join(context['domains'])}")
        print(f"    → Complexity: {context['complexity']}")
        print(f"    → Patterns: {', '.join(context['patterns'])}")
        
        # Generate cross-references
        cross_refs = cross_reference_system.generate_cross_references(context)
        if cross_refs:
            print(f"    🔗 Cross-references:")
            for ref in cross_refs[:2]:
                print(f"      • {ref['explanation']}")
        
        # Create contextual analogy
        analogy = cross_reference_system.create_contextual_analogy(topic, "technology")
        print(f"    💭 Analogy: {analogy}")

def demo_values():
    """Demonstrate values system"""
    print("\n" + "="*60)
    print("💎 VALUES SYSTEM DEMO")
    print("="*60)
    
    # Show core values
    print("\n📋 Core Values Alignment:")
    values = {
        "helpfulness": 0.9,
        "honesty": 0.9,
        "creativity": 0.8,
        "growth": 0.8,
        "empathy": 0.7,
        "curiosity": 0.9,
        "clarity": 0.8,
        "positivity": 0.7,
    }
    
    for value, strength in sorted(values.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(strength * 10)
        print(f"  {value:12} {bar} {strength:.1f}")
    
    # Test value alignment for actions
    actions = [
        "help user solve a problem",
        "create innovative solution",
        "explore new ideas",
        "provide honest feedback",
    ]
    
    print("\n🎯 Action-Value Alignment:")
    for action in actions:
        alignment = personality_engine.get_values_alignment(action)
        top_values = sorted(alignment.items(), key=lambda x: x[1], reverse=True)[:2]
        print(f"  '{action}' → {', '.join([f'{v} ({s:.1f})' for v, s in top_values])}")

def demo_friendly_correspondence():
    """Demonstrate friendly correspondence features"""
    print("\n" + "="*60)
    print("🤝 FRIENDLY CORRESPONDENCE DEMO")
    print("="*60)
    
    # Initialize assistant with all features
    try:
        assistant = EchoesAssistantV2(
            enable_rag=False,  # Disable for demo simplicity
            enable_tools=False,
            enable_streaming=False,
            enable_status=False,
        )
        
        # Friendly conversation examples
        friendly_inputs = [
            "Hey there! How are you doing today?",
            "I'm working on something creative and need inspiration!",
            "Can you help me understand this complex topic?",
            "I'm feeling a bit overwhelmed, can you guide me?",
        ]
        
        print("\n💬 Friendly Conversation Examples:")
        for user_msg in friendly_inputs:
            print(f"\n  User: {user_msg}")
            
            # Update personality based on message
            personality_engine.update_from_interaction(user_msg)
            
            # Generate a friendly response prefix
            prefix = personality_engine.generate_response_prefix("greeting")
            
            # Show mood adaptation
            stats = personality_engine.get_personality_summary()
            
            print(f"  Assistant: {prefix} I'm here to help! (Mood: {stats['current_mood']})")
            
    except Exception as e:
        print(f"  Note: Assistant initialization skipped for demo: {e}")

def main():
    """Run all demos"""
    print("\n✨ Welcome to the Enhanced Echoes Assistant Demo!")
    print("This showcases the new personality, error handling, and cross-reference features.")
    
    # Run all demos
    demo_personality()
    demo_error_handling()
    demo_cross_references()
    demo_values()
    demo_friendly_correspondence()
    
    print("\n" + "="*60)
    print("🎉 Demo Complete!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("  ✅ Dynamic personality adaptation based on user mood")
    print("  ✅ Automated error detection and fixing")
    print("  ✅ Intelligent cross-referencing across domains")
    print("  ✅ Values-driven response generation")
    print("  ✅ Friendly, engaging correspondence style")
    print("\nTry the interactive mode with:")
    print("  python assistant_v2_core.py")
    print("  Then try commands like: personality, fixes, crossref <topic>")

if __name__ == "__main__":
    main()
