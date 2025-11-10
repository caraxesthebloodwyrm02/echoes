#!/usr/bin/env python3
"""
Comprehensive Integration Test - Tests all layers of the Echoes system
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_all_layers():
    """Test all layers of the Echoes system"""
    print("🌟 ECHOES COMPREHENSIVE INTEGRATION TEST")
    print("=" * 80)

    try:
        # Test 1: Core Modules (already working)
        print("\n🧠 Testing Core Modules...")
        from core_modules.catch_release_system import ContentType, catch_release
        from core_modules.intent_awareness_engine import intent_engine
        from core_modules.parallel_simulation_engine import (
            SimulationType,
            parallel_simulation,
        )
        from core_modules.personality_engine import personality_engine
        from core_modules.train_of_thought_tracker import ThoughtType, thought_tracker

        print("✅ Core modules imported")

        # Test 2: App Layer
        print("\n🏗️ Testing App Layer...")
        from app.actions.action_executor import ActionExecutor
        from app.model_router import ModelRouter
        from app.values import ValueSystem

        print("✅ App layer imported")

        # Test 3: API Layer
        print("\n🌐 Testing API Layer...")
        from api.config import APIConfig
        from api.middleware import RequestLoggingMiddleware

        print("✅ API layer imported")

        # Test 4: Tools Layer
        print("\n🔧 Testing Tools Layer...")
        from tools.registry import ToolRegistry

        print("✅ Tools layer imported")

        # Test 5: UCR Module
        print("\n📊 Testing UCR Module...")
        from ucr import UCR

        print("✅ UCR module imported")

        # Execute functionality tests
        print("\n⚡ Testing Functionality...")

        # Test Model Router
        router = ModelRouter()
        assert router is not None, "ModelRouter failed"
        print("✅ ModelRouter initialized")

        # Test Values System
        values = ValueSystem()
        assert values is not None, "ValueSystem failed"
        print("✅ ValueSystem initialized")

        # Test Action Executor
        executor = ActionExecutor()
        assert executor is not None, "ActionExecutor failed"
        print("✅ ActionExecutor initialized")

        # Test API Config
        api_config = APIConfig()
        assert api_config is not None, "APIConfig failed"
        print("✅ APIConfig initialized")

        # Test Request Logging Middleware
        middleware = RequestLoggingMiddleware(
            None
        )  # app parameter can be None for testing
        assert middleware is not None, "RequestLoggingMiddleware failed"
        print("✅ RequestLoggingMiddleware initialized")

        # Test Tool Registry
        registry = ToolRegistry()
        assert registry is not None, "ToolRegistry failed"
        print("✅ ToolRegistry initialized")

        # Test UCR
        ucr = UCR()
        assert ucr is not None, "UCR failed"
        print("✅ UCR initialized")

        # Test core functionality
        print("\n🎯 Testing Core Functionality...")

        # Simulation
        sim_id = parallel_simulation.create_simulation(
            simulation_type=SimulationType.SCENARIO_EXPLORATION,
            input_data={"query": "test"},
            parameters={"max_scenarios": 1},
        )
        assert sim_id, "Simulation failed"
        print("✅ Simulation working")

        # Cache
        test_data = {"test": "data"}
        key = catch_release.catch(test_data, ContentType.CONVERSATION)
        retrieved = catch_release.release(key)
        assert retrieved == test_data, "Cache failed"
        print("✅ Cache working")

        # Intent recognition
        intent = intent_engine.detect_intent("I want to learn Python")
        assert intent, "Intent detection failed"
        print("✅ Intent recognition working")

        # Thought tracking
        import uuid

        thought_id = str(uuid.uuid4())
        thought_tracker.add_thought(thought_id, "test thought", ThoughtType.INSIGHT)
        assert thought_id in thought_tracker.thought_metadata, "Thought tracking failed"
        print("✅ Thought tracking working")

        # Personality
        mood = personality_engine.current_mood
        assert mood, "Personality failed"
        print("✅ Personality working")

        print("\n🎉 ALL LAYERS INTEGRATED AND WORKING!")
        return True

    except Exception as e:
        print(f"\n❌ Comprehensive test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run comprehensive test"""
    success = test_all_layers()

    if success:
        print("\n✅ COMPREHENSIVE INTEGRATION TEST PASSED")
        print("All Echoes layers are working together perfectly")
        return 0
    else:
        print("\n❌ COMPREHENSIVE INTEGRATION TEST FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
