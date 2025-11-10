"""Integration tests for the smart terminal."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from smart_terminal.core.feedback import FeedbackHandler
from smart_terminal.core.predictor import CommandPredictor
from smart_terminal.interface.terminal import TerminalInterface, TerminalPreset


class TestTerminalIntegration(unittest.TestCase):
    """Integration tests for the smart terminal components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.commands_file = Path(self.temp_dir.name) / "commands.json"
        self.feedback_file = Path(self.temp_dir.name) / "feedback.json"

        # Initialize components with test data files
        self.predictor = CommandPredictor(str(self.commands_file))
        self.feedback = FeedbackHandler(str(self.feedback_file))

        # Mock the terminal interface to avoid UI interactions
        with patch("prompt_toolkit.PromptSession"):
            self.terminal = TerminalInterface(self.predictor, self.feedback)
            self.terminal.session = MagicMock()
            self.terminal.session.prompt = MagicMock(return_value="exit")

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_command_prediction_flow(self):
        """Test the complete flow of command prediction and feedback."""
        # Add some commands to the predictor
        self.predictor.update_command("git status")
        self.predictor.update_command("git add .")
        self.predictor.update_command("ls -la")

        # Get suggestions
        suggestions = self.predictor.get_suggestions("git")
        self.assertIn("git status", suggestions)
        self.assertIn("git add .", suggestions)

        # Add feedback for suggestions
        self.feedback.add_suggestion("git status", accepted=True)
        self.feedback.add_suggestion("git add .", accepted=False)

        # Verify feedback was recorded
        self.assertEqual(len(self.feedback.feedback["suggestions"]), 2)

        # Save and reload
        self.predictor.save_commands()
        self.feedback.save_feedback()

        # Create new instances to test persistence
        new_predictor = CommandPredictor(str(self.commands_file))
        new_feedback = FeedbackHandler(str(self.feedback_file))

        # Verify data was saved and loaded correctly
        self.assertEqual(
            new_predictor.commands, {"git status": 1, "git add .": 1, "ls -la": 1}
        )
        self.assertEqual(len(new_feedback.feedback["suggestions"]), 2)

    @patch("os.chdir")
    @patch("subprocess.Popen")
    async def test_command_execution_flow(self, mock_popen, mock_chdir):
        """Test the complete flow of command execution."""
        # Mock the subprocess
        process_mock = MagicMock()
        process_mock.communicate.return_value = (b"test output", b"")
        process_mock.returncode = 0
        mock_popen.return_value = process_mock

        # Test a regular command
        output, exec_time = await self.terminal._execute_command("echo test")

        # Verify command was executed
        mock_popen.assert_called_once()
        self.assertEqual(output, "test output")
        self.assertGreater(exec_time, 0)

        # Test cd command
        await self.terminal._process_command("cd /test/dir")
        mock_chdir.assert_called_once_with("/test/dir")

    @patch("smart_terminal.interface.terminal.TerminalInterface._execute_command")
    async def test_terminal_ui_flow(self, mock_execute):
        """Test the terminal UI flow with mocked user input."""
        # Mock command execution
        mock_execute.return_value = ("command output", 0.1)

        # Mock user input sequence
        input_sequence = ["echo hello", "ls -la", "exit"]
        self.terminal.session.prompt_async.side_effect = input_sequence

        # Run the terminal
        await self.terminal.run_async()

        # Verify commands were processed
        self.assertEqual(mock_execute.call_count, 2)  # Should not process "exit"
        self.predictor.update_command.assert_any_call("echo hello")
        self.predictor.update_command.assert_any_call("ls -la")

    def test_preset_application(self):
        """Test applying different presets and their effects."""
        # Test Developer preset
        self.terminal.apply_preset(TerminalPreset.DEVELOPER)
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.SMART)
        self.assertTrue(self.terminal.show_typing_stats)

        # Test Writer preset
        self.terminal.apply_preset(TerminalPreset.WRITER)
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.FUZZY)
        self.assertFalse(self.terminal.show_typing_stats)

        # Test Admin preset
        self.terminal.apply_preset(TerminalPreset.ADMIN)
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.EXACT)
        self.assertTrue(self.terminal.show_command_history)

        # Test Data Science preset
        self.terminal.apply_preset(TerminalPreset.DATA_SCIENCE)
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.SMART)
        self.assertTrue(self.terminal.auto_complete)


if __name__ == "__main__":
    unittest.main()
