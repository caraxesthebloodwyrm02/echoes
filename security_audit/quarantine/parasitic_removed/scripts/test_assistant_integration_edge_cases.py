#!/usr/bin/env python3
"""
Edge Case Tests for Smart Terminal Integration with FusedAssistant

Tests integration edge cases between smart_terminal components and the assistant.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock the smart terminal availability
import smart_terminal

original_available = getattr(smart_terminal, "SMART_TERMINAL_AVAILABLE", True)


class TestAssistantIntegrationEdgeCases(unittest.TestCase):
    """Test edge cases for smart terminal integration with assistant."""

    def setUp(self):
        """Set up test fixtures."""
        # Force smart terminal availability for testing
        smart_terminal.SMART_TERMINAL_AVAILABLE = True

        # Import after setting availability
        from assistant import FusedAssistant

        self.assistant = FusedAssistant()

    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original availability
        smart_terminal.SMART_TERMINAL_AVAILABLE = original_available

    def test_assistant_initialization_with_smart_terminal(self):
        """Test assistant initialization with smart terminal components."""
        self.assertIsNotNone(self.assistant.smart_predictor)
        self.assertIsNotNone(self.assistant.smart_feedback)
        self.assertIsNotNone(self.assistant.smart_terminal)

    def test_smart_suggestions_with_empty_input(self):
        """Test smart suggestions with empty input."""
        suggestions = self.assistant.get_smart_suggestions("")
        self.assertIsInstance(suggestions, list)

    def test_smart_suggestions_with_none_input(self):
        """Test smart suggestions with None input."""
        suggestions = self.assistant.get_smart_suggestions(None)
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 0)

    def test_smart_feedback_with_invalid_data(self):
        """Test smart feedback with invalid data."""
        result = self.assistant.provide_smart_feedback("test_command", "invalid_rating")
        self.assertFalse(result)

    def test_smart_feedback_with_none_rating(self):
        """Test smart feedback with None rating."""
        result = self.assistant.provide_smart_feedback("test_command", None)
        self.assertTrue(result)  # Should succeed with general feedback

    @patch("smart_terminal.core.predictor.CommandPredictor.get_suggestions")
    def test_smart_suggestions_exception_handling(self, mock_get_suggestions):
        """Test smart suggestions exception handling."""
        mock_get_suggestions.side_effect = Exception("Test exception")

        suggestions = self.assistant.get_smart_suggestions("test")
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 0)

    @patch("smart_terminal.core.feedback.FeedbackHandler.add_rating")
    def test_smart_feedback_exception_handling(self, mock_add_rating):
        """Test smart feedback exception handling."""
        mock_add_rating.side_effect = Exception("Test exception")

        result = self.assistant.provide_smart_feedback("test_command", 3)
        self.assertFalse(result)

    @patch("smart_terminal.interface.terminal.TerminalInterface.run")
    def test_smart_terminal_mode_exception_handling(self, mock_run):
        """Test smart terminal mode exception handling."""
        mock_run.side_effect = Exception("Test exception")

        with patch("builtins.print"):
            try:
                self.assistant.start_smart_terminal_mode()
            except Exception:
                self.fail("Should handle smart terminal exceptions gracefully")

    def test_assistant_command_execution_with_smart_feedback(self):
        """Test that command execution provides feedback to smart terminal."""
        # Execute a command
        result = self.assistant.execute_command("echo test")

        # Should have provided feedback to smart terminal
        self.assertTrue(result.success)

    def test_assistant_suggestions_include_smart_suggestions(self):
        """Test that assistant suggestions include smart terminal suggestions."""
        result = self.assistant.execute_command("invalid_command")

        # Should include suggestions even for failed commands
        self.assertIsInstance(result.suggestions, list)

    def test_smart_terminal_unavailable_graceful_degradation(self):
        """Test graceful degradation when smart terminal is unavailable."""
        # Temporarily disable smart terminal
        smart_terminal.SMART_TERMINAL_AVAILABLE = False

        # Reload assistant components (simulate reinitialization)
        self.assistant.smart_predictor = None
        self.assistant.smart_feedback = None
        self.assistant.smart_terminal = None

        # Test methods still work
        suggestions = self.assistant.get_smart_suggestions("test")
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 0)

        result = self.assistant.provide_smart_feedback("test", 3)
        self.assertFalse(result)

        # Should not crash when trying to start smart terminal mode
        try:
            self.assistant.start_smart_terminal_mode()
        except Exception:
            self.fail("Should handle unavailable smart terminal gracefully")

    def test_concurrent_smart_terminal_operations(self):
        """Test concurrent smart terminal operations."""
        import threading
        import time

        results = []

        def worker(thread_id):
            for i in range(10):
                suggestions = self.assistant.get_smart_suggestions(
                    f"cmd_{thread_id}_{i}"
                )
                results.append(len(suggestions))
                time.sleep(0.01)

        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have completed without errors
        self.assertEqual(len(results), 30)

    def test_smart_terminal_memory_pressure(self):
        """Test smart terminal under memory pressure."""
        # Generate many suggestions and feedback
        for i in range(100):
            self.assistant.get_smart_suggestions(f"memory_test_command_{i}")
            self.assistant.provide_smart_feedback(f"memory_test_cmd_{i}", (i % 5) + 1)

        # Should still function normally
        suggestions = self.assistant.get_smart_suggestions("final_test")
        self.assertIsInstance(suggestions, list)

    def test_smart_terminal_large_input_handling(self):
        """Test smart terminal with very large inputs."""
        large_input = "command " * 1000  # Very long command
        suggestions = self.assistant.get_smart_suggestions(large_input)
        self.assertIsInstance(suggestions, list)

        result = self.assistant.provide_smart_feedback(large_input, 3)
        # Should handle gracefully (may fail due to length, but not crash)
        self.assertIsInstance(result, bool)


class TestAssistantIntegrationWithoutSmartTerminal(unittest.TestCase):
    """Test assistant integration when smart terminal is not available."""

    def setUp(self):
        """Set up test fixtures without smart terminal."""
        from assistant import FusedAssistant

        self.assistant = FusedAssistant()

        # Manually disable smart terminal components for testing
        self.assistant.smart_predictor = None
        self.assistant.smart_feedback = None
        self.assistant.smart_terminal = None

    def test_assistant_without_smart_terminal(self):
        """Test that assistant works normally without smart terminal."""
        self.assertIsNone(self.assistant.smart_predictor)
        self.assertIsNone(self.assistant.smart_feedback)
        self.assertIsNone(self.assistant.smart_terminal)

        # Should still function normally
        result = self.assistant.execute_command("echo test")
        self.assertTrue(result.success)

        suggestions = self.assistant.get_smart_suggestions("test")
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 0)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
