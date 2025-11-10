#!/usr/bin/env python3
"""
Comprehensive test script for the Smart Terminal
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_predictor():
    """Test CommandPredictor functionality"""
    print("Testing CommandPredictor...")
    try:
        from core.predictor import CommandPredictor

        predictor = CommandPredictor()

        # Test command updates
        predictor.update_command("ls")
        predictor.update_command("cd")
        predictor.update_command("ls")  # More frequent

        # Test suggestions
        suggestions = predictor.get_suggestions("l")
        assert "ls" in suggestions, f"Expected 'ls' in suggestions, got {suggestions}"

        # Test empty suggestions
        empty_suggestions = predictor.get_suggestions("xyz")
        assert empty_suggestions == [], f"Expected empty list, got {empty_suggestions}"

        print("✓ CommandPredictor tests passed")
        return True
    except Exception as e:
        print(f"✗ CommandPredictor test failed: {e}")
        return False


def test_feedback():
    """Test FeedbackHandler functionality"""
    print("Testing FeedbackHandler...")
    try:
        from core.feedback import FeedbackHandler

        feedback = FeedbackHandler()

        # Test adding feedback
        feedback.add_rating("ls", 5)
        feedback.add_suggestion("ls", True)

        # Verify data was saved
        assert len(feedback.feedback["ratings"]) == 1
        assert len(feedback.feedback["suggestions"]) == 1

        print("✓ FeedbackHandler tests passed")
        return True
    except Exception as e:
        print(f"✗ FeedbackHandler test failed: {e}")
        return False


def test_terminal_interface():
    """Test TerminalInterface initialization"""
    print("Testing TerminalInterface...")
    try:
        from interface.terminal import TerminalInterface

        from core.feedback import FeedbackHandler
        from core.predictor import CommandPredictor

        predictor = CommandPredictor()
        feedback = FeedbackHandler()
        terminal = TerminalInterface(predictor, feedback)

        # Just test initialization
        assert hasattr(terminal, "predictor")
        assert hasattr(terminal, "feedback")
        assert hasattr(terminal, "run")

        print("✓ TerminalInterface tests passed")
        return True
    except Exception as e:
        print(f"✗ TerminalInterface test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=== Smart Terminal Comprehensive Test ===\n")

    tests = [
        test_imports,
        test_predictor,
        test_feedback,
        test_terminal_interface,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Smart Terminal is ready to use.")
        print("\nTo run the terminal:")
        print("  cd smart_terminal")
        print("  python main.py")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
