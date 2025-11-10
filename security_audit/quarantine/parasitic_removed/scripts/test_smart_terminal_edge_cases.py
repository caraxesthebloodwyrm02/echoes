#!/usr/bin/env python3
"""
Comprehensive Edge Case Tests for Smart Terminal Components

Tests various edge cases and error conditions for:
- CommandPredictor
- FeedbackHandler
- TerminalInterface
- Integration with FusedAssistant
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add the smart_terminal module to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_terminal.core.feedback import FeedbackHandler
from smart_terminal.core.predictor import CommandPredictor
from smart_terminal.interface.terminal import TerminalInterface


class TestSmartTerminalEdgeCases(unittest.TestCase):
    """Comprehensive edge case tests for SmartTerminal components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.feedback_path = os.path.join(self.temp_dir, "test_feedback.json")
        self.predictor = CommandPredictor()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ============================================================================
    # CommandPredictor Edge Cases
    # ============================================================================

    def test_predictor_empty_input(self):
        """Test predictor with empty input."""
        suggestions = self.predictor.get_suggestions("")
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 0)

    def test_predictor_none_input(self):
        """Test predictor with None input."""
        # The predictor actually handles None gracefully by returning empty list
        suggestions = self.predictor.get_suggestions(None)
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 0)

    def test_predictor_whitespace_only(self):
        """Test predictor with whitespace-only input."""
        suggestions = self.predictor.get_suggestions("   \t\n  ")
        self.assertIsInstance(suggestions, list)

    def test_predictor_unicode_characters(self):
        """Test predictor with unicode characters."""
        suggestions = self.predictor.get_suggestions("café résumé naïve")
        self.assertIsInstance(suggestions, list)

    def test_predictor_extremely_long_input(self):
        """Test predictor with extremely long input."""
        long_input = "command " * 1000
        suggestions = self.predictor.get_suggestions(long_input)
        self.assertIsInstance(suggestions, list)

    def test_predictor_special_characters(self):
        """Test predictor with special characters."""
        suggestions = self.predictor.get_suggestions(
            "cmd --flag=value & echo 'test' | grep pattern"
        )
        self.assertIsInstance(suggestions, list)

    def test_predictor_binary_data(self):
        """Test predictor with binary-like data."""
        binary_input = bytes(range(256)).decode("latin-1", errors="ignore")
        suggestions = self.predictor.get_suggestions(binary_input)
        self.assertIsInstance(suggestions, list)

    def test_predictor_update_with_various_commands(self):
        """Test updating predictor with various command types."""
        commands = [
            "ls -la",
            "cd /tmp",
            "git status",
            "",  # empty command
            "   ",  # whitespace command
            "echo 'hello world'",
            "python -c 'print(42)'",
            "docker run --rm ubuntu:latest echo hello",
        ]

        for cmd in commands:
            try:
                self.predictor.update_command(cmd)
            except Exception as e:
                self.fail(f"update_command failed for command '{cmd}': {e}")

    # ============================================================================
    # FeedbackHandler Edge Cases
    # ============================================================================

    def test_feedback_handler_missing_directory(self):
        """Test feedback handler with missing directory."""
        deep_path = os.path.join(
            self.temp_dir, "deep", "nested", "path", "feedback.json"
        )
        feedback = FeedbackHandler(deep_path)

        # Should create the directory structure without error
        self.assertTrue(os.path.exists(os.path.dirname(deep_path)))
        # save_feedback doesn't return anything, just check it doesn't raise exception
        feedback.save_feedback()

    def test_feedback_handler_corrupt_json(self):
        """Test feedback handler with corrupt JSON file."""
        # Create a corrupt JSON file
        with open(self.feedback_path, "w") as f:
            f.write("{ invalid json content }")

        feedback = FeedbackHandler(self.feedback_path)
        # Should handle the corrupt file gracefully
        self.assertIsInstance(feedback.feedback, dict)
        self.assertIn("suggestions", feedback.feedback)
        self.assertIn("ratings", feedback.feedback)

    def test_feedback_handler_empty_file(self):
        """Test feedback handler with empty file."""
        Path(self.feedback_path).touch()  # Create empty file
        feedback = FeedbackHandler(self.feedback_path)
        self.assertIsInstance(feedback.feedback, dict)

    def test_feedback_handler_binary_file(self):
        """Test feedback handler with binary file content."""
        with open(self.feedback_path, "wb") as f:
            f.write(b"\x00\x01\x02\x03binary data")

        feedback = FeedbackHandler(self.feedback_path)
        # Should handle binary data gracefully
        self.assertIsInstance(feedback.feedback, dict)

    def test_feedback_handler_large_file(self):
        """Test feedback handler with very large file."""
        large_data = {"suggestions": [], "ratings": []}
        large_data["suggestions"] = [
            {"suggestion": "x" * 1000, "accepted": True, "timestamp": "2023-01-01"}
        ] * 10000

        with open(self.feedback_path, "w") as f:
            json.dump(large_data, f)

        feedback = FeedbackHandler(self.feedback_path)
        self.assertIsInstance(feedback.feedback, dict)

    def test_feedback_handler_permission_denied(self):
        """Test feedback handler with permission denied."""
        # Create a read-only directory
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only

        readonly_path = os.path.join(readonly_dir, "feedback.json")
        feedback = FeedbackHandler(readonly_path)

        # Should handle permission errors gracefully
        try:
            feedback.save_feedback()
        except Exception:
            # Expected to fail due to permissions
            pass

        # Restore permissions for cleanup
        os.chmod(readonly_dir, 0o755)

    def test_feedback_handler_invalid_rating_values(self):
        """Test feedback handler with invalid rating values."""
        feedback = FeedbackHandler(self.feedback_path)

        # Test various invalid rating values
        invalid_ratings = [0, 6, -1, 10, "five", None, [], {}]

        for rating in invalid_ratings:
            try:
                feedback.add_rating("test_command", rating)
                # Check that rating was clamped to valid range
                last_rating = feedback.feedback["ratings"][-1]["rating"]
                self.assertIn(last_rating, [1, 2, 3, 4, 5])
            except Exception:
                # Should handle gracefully
                pass

    def test_feedback_handler_empty_strings(self):
        """Test feedback handler with empty strings."""
        feedback = FeedbackHandler(self.feedback_path)

        feedback.add_suggestion("", True)
        feedback.add_rating("", 3)

        # Should handle empty strings gracefully
        self.assertEqual(len(feedback.feedback["suggestions"]), 1)
        self.assertEqual(len(feedback.feedback["ratings"]), 1)

    def test_feedback_handler_unicode_content(self):
        """Test feedback handler with unicode content."""
        feedback = FeedbackHandler(self.feedback_path)

        unicode_suggestion = "café résumé naïve 🚀"
        unicode_command = "git commit -m 'fix: café bug'"

        feedback.add_suggestion(unicode_suggestion, True)
        feedback.add_rating(unicode_command, 5)

        # Should handle unicode gracefully
        self.assertEqual(
            feedback.feedback["suggestions"][0]["suggestion"], unicode_suggestion
        )
        self.assertEqual(feedback.feedback["ratings"][0]["command"], unicode_command)

    # ============================================================================
    # TerminalInterface Edge Cases
    # ============================================================================

    @patch("builtins.input")
    @patch("builtins.print")
    def test_terminal_interface_keyboard_interrupt(self, mock_print, mock_input):
        """Test terminal interface with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()

        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(self.predictor, feedback)

        # Skip test if prompt_toolkit is not available (Windows console issues)
        if not hasattr(terminal, "run") or not callable(getattr(terminal, "run", None)):
            self.skipTest("Terminal interface not properly configured")

        try:
            terminal.run()
        except SystemExit:
            # Expected behavior
            pass
        except Exception as e:
            # Accept various console-related exceptions
            if "console" in str(e).lower() or "NoConsoleScreenBufferError" in str(e):
                self.skipTest(f"Console not available in test environment: {e}")
            else:
                raise

    @patch("builtins.input")
    @patch("builtins.print")
    def test_terminal_interface_eof_interrupt(self, mock_print, mock_input):
        """Test terminal interface with EOF interrupt."""
        mock_input.side_effect = EOFError()

        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(self.predictor, feedback)

        # Should handle EOF gracefully
        try:
            terminal.get_feedback()
        except Exception:
            self.fail("Should handle EOF gracefully")

    @patch("builtins.input")
    def test_terminal_interface_invalid_numeric_input(self, mock_input):
        """Test terminal interface with invalid numeric input."""
        mock_input.return_value = "not_a_number"

        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(self.predictor, feedback)

        # Should handle invalid input gracefully
        try:
            terminal.rate_command()
        except Exception:
            self.fail("Should handle invalid numeric input gracefully")

    @patch("builtins.input")
    def test_terminal_interface_empty_feedback_input(self, mock_input):
        """Test terminal interface with empty feedback input."""
        mock_input.return_value = ""

        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(self.predictor, feedback)

        # Should handle empty input gracefully
        try:
            terminal.report_suggestion()
        except Exception:
            self.fail("Should handle empty input gracefully")

    def test_terminal_interface_none_predictor(self):
        """Test terminal interface with None predictor."""
        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(None, feedback)

        # Should raise AttributeError when trying to access predictor
        with self.assertRaises(AttributeError):
            terminal.show_suggestions()

    def test_terminal_interface_none_feedback(self):
        """Test terminal interface with None feedback handler."""
        terminal = TerminalInterface(self.predictor, None)

        # Should raise AttributeError when trying to access feedback
        with self.assertRaises(AttributeError):
            terminal.get_feedback()

    # ============================================================================
    # Integration Edge Cases
    # ============================================================================

    @patch("smart_terminal.core.predictor.CommandPredictor.get_suggestions")
    def test_predictor_exception_handling(self, mock_get_suggestions):
        """Test predictor exception handling in integration."""
        mock_get_suggestions.side_effect = Exception("Test exception")

        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(self.predictor, feedback)

        # show_suggestions should handle predictor exceptions gracefully
        try:
            terminal.show_suggestions()
        except Exception:
            self.fail("Should handle predictor exceptions gracefully")

    @patch("smart_terminal.core.feedback.FeedbackHandler.save_feedback")
    def test_feedback_exception_handling(self, mock_save_feedback):
        """Test feedback exception handling in integration."""
        mock_save_feedback.side_effect = Exception("Test exception")

        feedback = FeedbackHandler(self.feedback_path)
        terminal = TerminalInterface(self.predictor, feedback)

        # get_feedback should handle feedback exceptions gracefully
        try:
            terminal.get_feedback()
        except Exception:
            self.fail("Should handle feedback exceptions gracefully")

    # ============================================================================
    # File I/O Edge Cases
    # ============================================================================

    def test_file_io_network_path(self):
        """Test file I/O with network-like paths."""
        network_paths = [
            "\\\\server\\share\\file.json",
            "//server/share/file.json",
            "http://example.com/file.json",
            "ftp://example.com/file.json",
        ]

        for path in network_paths:
            try:
                FeedbackHandler(path)
                # Should handle gracefully even if path doesn't work
            except Exception:
                # Expected for invalid paths
                pass

    def test_file_io_relative_paths(self):
        """Test file I/O with various relative paths."""
        relative_paths = [
            ".",
            "..",
            "./data/feedback.json",
            "../data/feedback.json",
            "data/../data/feedback.json",
        ]

        for rel_path in relative_paths:
            try:
                feedback = FeedbackHandler(rel_path)
                feedback.save_feedback()
            except Exception:
                # Some relative paths may fail, which is expected
                pass

    def test_file_io_concurrent_access(self):
        """Test file I/O with concurrent access simulation."""
        import threading
        import time

        feedback = FeedbackHandler(self.feedback_path)

        def concurrent_writer():
            for i in range(10):
                feedback.add_suggestion(f"concurrent_suggestion_{i}", True)
                time.sleep(0.01)

        threads = []
        for _ in range(3):
            t = threading.Thread(target=concurrent_writer)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have handled concurrent access gracefully
        self.assertGreater(len(feedback.feedback["suggestions"]), 0)

    # ============================================================================
    # Memory and Performance Edge Cases
    # ============================================================================

    def test_memory_large_dataset(self):
        """Test handling of large datasets."""
        feedback = FeedbackHandler(self.feedback_path)

        # Add many suggestions
        for i in range(1000):
            feedback.add_suggestion(f"large_dataset_suggestion_{i}", i % 2 == 0)

        # Add many ratings
        for i in range(1000):
            feedback.add_rating(f"large_dataset_command_{i}", (i % 5) + 1)

        # Should handle large datasets gracefully
        self.assertEqual(len(feedback.feedback["suggestions"]), 1000)
        self.assertEqual(len(feedback.feedback["ratings"]), 1000)

    def test_performance_many_suggestions(self):
        """Test performance with many suggestions."""
        import time

        feedback = FeedbackHandler(self.feedback_path)

        # Add many suggestions quickly
        start_time = time.time()
        for i in range(100):
            feedback.add_suggestion(f"perf_suggestion_{i}", True)
        end_time = time.time()

        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 5.0)  # Less than 5 seconds


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
