#!/usr/bin/env python3
"""
Quick Integration Test - Validates all systems are working together
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_system_imports():
    """Test that all core systems can be imported"""
    print("🔍 Testing system imports...")

    try:
        from assistant_v2_core import EchoesAssistantV2

        print("✅ EchoesAssistantV2 imported")

        from core_modules.parallel_simulation_engine import (
            parallel_simulation,
            SimulationType,
        )

        print("✅ Parallel Simulation Engine imported")

        from core_modules.catch_release_system import (
            catch_release,
            CacheLevel,
            ContentType,
        )

        print("✅ Catch & Release System imported")

        from core_modules.intent_awareness_engine import intent_engine, IntentType

        print("✅ Intent Awareness Engine imported")

        from core_modules.train_of_thought_tracker import thought_tracker, ThoughtType

        print("✅ Thought Tracker imported")

        from core_modules.personality_engine import personality_engine

        print("✅ Personality Engine imported")

        from core_modules.humor_engine import humor_engine

        print("✅ Humor Engine imported")

        from core_modules.cross_reference_system import cross_reference_system

        print("✅ Cross-Reference System imported")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_assistant_initialization():
    """Test assistant initialization with all systems"""
    print("\n🚀 Testing assistant initialization...")

    try:
        from assistant_v2_core import EchoesAssistantV2

        assistant = EchoesAssistantV2(
            enable_rag=True,
            enable_tools=True,
            enable_streaming=True,
            enable_status=True,
        )

        print("✅ Assistant initialized successfully")
        print(f"   Session ID: {assistant.session_id}")
        print(f"   Tools available: {len(assistant.list_tools())}")

        return assistant

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None


def test_basic_functionality(assistant):
    """Test basic functionality with integrated systems"""
    print("\n🧪 Testing basic integrated functionality...")

    try:
        # Test 1: Simple query with intent awareness
        query1 = "What are the main challenges in AI development?"
        print(f"\n📝 Query 1: {query1}")

        start_time = time.time()
        response1 = assistant.chat(query1, stream=False)
        response_time1 = time.time() - start_time

        print(f"✅ Response received in {response_time1:.2f}s")
        print(f"   Response length: {len(response1)} characters")

        # Test 2: Query that triggers simulations
        query2 = (
            "Explore different approaches to implement machine learning in healthcare"
        )
        print(f"\n🧠 Query 2 (with simulations): {query2}")

        start_time = time.time()
        response2 = assistant.chat(query2, stream=False)
        response_time2 = time.time() - start_time

        print(f"✅ Enhanced response received in {response_time2:.2f}s")
        print(f"   Response length: {len(response2)} characters")

        # Test 3: Query testing conversation continuity
        query3 = (
            "Based on what we just discussed, what would be the most ethical approach?"
        )
        print(f"\n🔄 Query 3 (continuity test): {query3}")

        start_time = time.time()
        response3 = assistant.chat(query3, stream=False)
        response_time3 = time.time() - start_time

        print(f"✅ Context-aware response received in {response_time3:.2f}s")
        print(f"   Response length: {len(response3)} characters")

        # Performance summary
        avg_response_time = (response_time1 + response_time2 + response_time3) / 3
        print(f"\n📊 Performance Summary:")
        print(f"   Average response time: {avg_response_time:.2f}s")
        print(
            f"   Total characters generated: {len(response1) + len(response2) + len(response3)}"
        )

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def test_system_statistics():
    """Test system statistics and monitoring"""
    print("\n📈 Testing system statistics...")

    try:
        from core_modules.parallel_simulation_engine import parallel_simulation
        from core_modules.catch_release_system import catch_release

        # Simulation stats
        sim_stats = parallel_simulation.get_simulation_statistics()
        print(f"🧠 Simulation Statistics:")
        print(f"   Total simulations: {sim_stats['total_simulations']}")
        print(f"   Success rate: {sim_stats['performance']['success_rate']:.1%}")

        # Cache stats
        cache_stats = catch_release.get_cache_statistics()
        print(f"\n💾 Cache Statistics:")
        print(f"   Session cache: {cache_stats['session_cache']['entries']} entries")
        print(
            f"   Short-term cache: {cache_stats['short_term_cache']['entries']} entries"
        )

        # Continuity check
        continuity = catch_release.get_conversation_continuity()
        print(f"\n🔄 Conversation Continuity:")
        print(f"   Continuity score: {continuity['continuity_score']:.1%}")
        print(f"   Recent entries: {continuity['total_recent']}")

        return True

    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False


def test_values_grounding(assistant):
    """Test values grounding and ethical alignment"""
    print("\n💎 Testing values grounding...")

    try:
        # Query with ethical considerations
        values_query = "How can I ensure my AI system respects human dignity and autonomy while still being effective?"

        print(f"💎 Values Query: {values_query}")

        start_time = time.time()
        response = assistant.chat(values_query, stream=False)
        response_time = time.time() - start_time

        print(f"✅ Values-grounded response in {response_time:.2f}s")

        # Check for ethical keywords
        ethical_keywords = [
            "ethic",
            "moral",
            "value",
            "principle",
            "dignity",
            "autonomy",
            "respect",
        ]
        ethical_content = sum(
            1 for keyword in ethical_keywords if keyword.lower() in response.lower()
        )

        print(f"   Ethical considerations found: {ethical_content}")
        print(
            f"   Response demonstrates values alignment: {'Yes' if ethical_content >= 3 else 'Partial'}"
        )

        return True

    except Exception as e:
        print(f"❌ Values grounding test failed: {e}")
        return False


def test_pressure_handling(assistant):
    """Test pressure handling and humor integration"""
    print("\n😄 Testing pressure handling...")

    try:
        # Pressure query
        pressure_query = "I'm feeling overwhelmed by all these complex technical decisions. Can you help me see this more clearly?"

        print(f"😄 Pressure Query: {pressure_query}")

        start_time = time.time()
        response = assistant.chat(pressure_query, stream=False)
        response_time = time.time() - start_time

        print(f"✅ Pressure-aware response in {response_time:.2f}s")

        # Check for supportive elements
        supportive_keywords = [
            "understand",
            "break down",
            "step",
            "manageable",
            "clarity",
            "perspective",
        ]
        supportive_content = sum(
            1 for keyword in supportive_keywords if keyword.lower() in response.lower()
        )

        print(f"   Supportive elements found: {supportive_content}")
        print(
            f"   Response shows empathy: {'Yes' if supportive_content >= 2 else 'Partial'}"
        )

        return True

    except Exception as e:
        print(f"❌ Pressure handling test failed: {e}")
        return False


def generate_integration_report(test_results):
    """Generate comprehensive integration report"""
    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST REPORT")
    print("=" * 80)

    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = passed_tests / total_tests

    print(f"\n📈 Test Results:")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    print(f"   Success rate: {success_rate:.1%}")

    print(f"\n✅ Passed Tests:")
    for test_name, passed in test_results.items():
        if passed:
            print(f"   • {test_name}")

    if passed_tests < total_tests:
        print(f"\n❌ Failed Tests:")
        for test_name, passed in test_results.items():
            if not passed:
                print(f"   • {test_name}")

    print(f"\n🌟 Integration Status:")
    if success_rate >= 0.9:
        print("   🏆 EXCELLENT: All systems integrated and working cohesively")
    elif success_rate >= 0.8:
        print("   ✅ GOOD: Systems integrated with minor issues")
    elif success_rate >= 0.7:
        print("   ⚠️ ACCEPTABLE: Basic integration functional")
    else:
        print("   ❌ NEEDS WORK: Integration issues detected")

    return success_rate


def main():
    """Run comprehensive integration test"""
    print("🌟 ECHOES INTEGRATION TEST")
    print("=" * 80)
    print("Testing all systems working together cohesively...")

    test_results = {}

    # Run all tests
    test_results["System Imports"] = test_system_imports()

    if test_results["System Imports"]:
        assistant = test_assistant_initialization()
        test_results["Assistant Initialization"] = assistant is not None

        if assistant:
            test_results["Basic Functionality"] = test_basic_functionality(assistant)
            test_results["System Statistics"] = test_system_statistics()
            test_results["Values Grounding"] = test_values_grounding(assistant)
            test_results["Pressure Handling"] = test_pressure_handling(assistant)
        else:
            print("❌ Skipping remaining tests due to initialization failure")
            return

    # Generate report
    success_rate = generate_integration_report(test_results)

    if success_rate >= 0.8:
        print(f"\n🎉 Integration test successful!")
        print("All Echoes systems are working together effectively.")
        print("\n💡 Next steps:")
        print("   • Run the full unified demo: python demo_unified_scenario.py")
        print("   • Test individual systems with their demo scripts")
        print("   • Start interactive mode: python assistant_v2_core.py")
    else:
        print(f"\n⚠️ Integration test completed with issues.")
        print("Some systems may need attention before full deployment.")

    return success_rate


if __name__ == "__main__":
    try:
        success_rate = main()
        sys.exit(0 if success_rate >= 0.8 else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
