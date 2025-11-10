"""Unit tests for TerminalInterface class."""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock prompt_toolkit before importing TerminalInterface
mock_pt = MagicMock()
mock_pt.__class__.__name__ = "MagicMock"
sys.modules["prompt_toolkit"] = mock_pt

# Import after mocking to ensure proper fallback
from smart_terminal.interface.terminal import (
    TerminalInterface,
    TerminalPreset,
    PROMPT_TOOLKIT_AVAILABLE,
)

from smart_terminal.interface.constants import SuggestionMode


class TestTerminalInterface(unittest.TestCase):
    """Test cases for TerminalInterface class."""

    def setUp(self):
        """Set up test environment."""
        self.predictor = MagicMock()
        self.feedback = MagicMock()

        # Create terminal interface - should use basic mode due to mocked prompt_toolkit
        self.terminal = TerminalInterface(self.predictor, self.feedback)

    def test_prompt_toolkit_availability(self):
        """Verify that prompt_toolkit is detected as unavailable in tests."""
        self.assertFalse(PROMPT_TOOLKIT_AVAILABLE)

    def test_basic_terminal_mode(self):
        """Test that basic terminal mode is used when prompt_toolkit is unavailable."""
        self.assertIsNotNone(self.terminal._session)
        self.assertFalse(hasattr(self.terminal, "_completer"))

    def test_initialization(self):
        """Test terminal interface initialization."""
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.SMART)
        self.assertIsInstance(self.terminal._session, MagicMock)

    def test_basic_terminal_functionality(self):
        """Test basic terminal functionality when prompt_toolkit is unavailable."""
        with patch("builtins.input", return_value="exit"):
            with patch("builtins.print") as mock_print:
                self.terminal._run_basic()
                mock_print.assert_called()

    def test_command_execution(self):
        """Test command execution in basic mode."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = b"test output"
            mock_run.return_value.returncode = 0

            with patch("builtins.print") as mock_print:
                self.terminal._execute_command("echo test")
                mock_print.assert_called()
                mock_run.assert_called_once()

    def test_error_handling(self):
        """Test error handling in basic mode."""
        # Initial mode is FUZZY
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.FUZZY)

        # First toggle - should be EXACT
        self.terminal._toggle_suggestion_mode()
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.EXACT)

        # Second toggle - should be SMART
        self.terminal._toggle_suggestion_mode()
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.SMART)

        # Third toggle - should wrap around to FUZZY
        self.terminal._toggle_suggestion_mode()
        self.assertEqual(self.terminal.suggestion_mode, SuggestionMode.FUZZY)

    @patch("asyncio.get_event_loop")
    async def test_run_async(self, mock_loop):
        """Test async run method."""
        # Mock the prompt to return 'exit' on first call
        self.terminal.session.prompt_async = MagicMock(return_value="exit")

        # Run the async method
        await self.terminal.run_async()

        # Verify the prompt was called
        self.terminal.session.prompt_async.assert_called_once()

    @patch("asyncio.get_event_loop")
    async def test_process_command_exit(self, mock_loop):
        """Test processing the exit command."""
        # This should not raise SystemExit because we're in a test
        with self.assertRaises(ValueError):  # Mocked exit raises ValueError
            await self.terminal._process_command("exit")

    @patch(
        "asyncio.sleep", return_value=None
    )  # Speed up tests by not actually sleeping
    async def test_show_loading(self, mock_sleep):
        """Test the loading indicator context manager."""
        async with self.terminal._show_loading():
            # The context manager should set and clear the loading state
            self.assertTrue(hasattr(self.terminal, "_loading"))
        self.assertFalse(hasattr(self.terminal, "_loading"))

    def test_get_prompt(self):
        """Test getting the prompt text."""
        # Mock the current working directory
        with patch("os.getcwd", return_value="/test/dir"):
            prompt = self.terminal._get_prompt()
            self.assertIn("/test/dir", prompt)
            self.assertIn("❯", prompt)  # Should contain the prompt character

    def test_get_status_bar(self):
        """Test getting the status bar content."""
        # Set some test values
        self.terminal.suggestion_mode = SuggestionMode.SMART
        self.terminal._typing_speed = 45.5
        self.terminal.current_preset = TerminalPreset.DEVELOPER

        status = self.terminal._get_status_bar()
        self.assertIn("SMART", status)
        self.assertIn("45.5", status)
        self.assertIn("Developer", status)

    def test_show_help(self):
        """Test the help text generation."""
        help_text = self.terminal._show_help()
        self.assertIn("Available Commands:", help_text)
        self.assertIn("F1", help_text)  # Should contain help shortcut
        self.assertIn("F2", help_text)  # Should contain history shortcut

    @patch("smart_terminal.interface.terminal.TerminalInterface._execute_command")
    async def test_process_command_cd(self, mock_execute):
        """Test processing a cd command."""
        mock_execute.return_value = ("", 0.1)  # Mock the command execution

        with patch("os.chdir") as mock_chdir:
            await self.terminal._process_command("cd /test/dir")
            mock_chdir.assert_called_once_with("/test/dir")

    @patch("smart_terminal.interface.terminal.TerminalInterface._execute_command")
    async def test_process_command_regular(self, mock_execute):
        """Test processing a regular command."""
        mock_execute.return_value = ("test output\nwith multiple lines", 0.1)

        with patch("builtins.print") as mock_print:
            await self.terminal._process_command("echo test")

            # Verify the command was executed and output was printed
            mock_execute.assert_called_once_with("echo test")
            mock_print.assert_called()

            # Verify the predictor was updated with the command
            self.predictor.update_command.assert_called_once_with("echo test")


if __name__ == "__main__":
    unittest.main()
