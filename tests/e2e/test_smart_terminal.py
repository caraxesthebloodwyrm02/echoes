"""End-to-end tests for the smart terminal."""
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from smart_terminal.core.feedback import FeedbackHandler
from smart_terminal.core.predictor import CommandPredictor
from smart_terminal.interface.terminal import TerminalInterface, TerminalPreset


class TestSmartTerminalE2E:
    """End-to-end tests for the smart terminal application."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment."""
        self.temp_dir = tmp_path
        self.commands_file = self.temp_dir / "commands.json"
        self.feedback_file = self.temp_dir / "feedback.json"

        # Set up environment variables
        self.original_env = os.environ.copy()
        os.environ["SMART_TERMINAL_COMMANDS_FILE"] = str(self.commands_file)
        os.environ["SMART_TERMINAL_FEEDBACK_FILE"] = str(self.feedback_file)

        yield

        # Clean up
        os.environ = self.original_env

    def test_command_prediction_workflow(self):
        """Test the complete workflow of command prediction and feedback."""
        # Initialize components
        predictor = CommandPredictor(str(self.commands_file))
        feedback = FeedbackHandler(str(self.feedback_file))

        # Add some commands
        test_commands = ["git status", "git add .", "ls -la", "python --version"]
        for cmd in test_commands:
            predictor.update_command(cmd)

        # Save and reload
        predictor.save_commands()

        # Test suggestions
        suggestions = predictor.get_suggestions("git")
        assert "git status" in suggestions
        assert "git add ." in suggestions

        # Add feedback
        feedback.add_suggestion("git status", accepted=True)
        feedback.add_suggestion("git add .", accepted=False)
        feedback.save_feedback()

        # Verify feedback was saved
        assert os.path.exists(self.feedback_file)
        with open(self.feedback_file, "r", encoding="utf-8") as f:
            feedback_data = json.load(f)
            assert len(feedback_data["suggestions"]) == 2

    @pytest.mark.asyncio
    async def test_terminal_interaction(self):
        """Test terminal interaction with mocked user input."""
        # Initialize components
        predictor = CommandPredictor(str(self.commands_file))
        feedback = FeedbackHandler(str(self.feedback_file))

        # Create terminal with mocked session
        with patch("prompt_toolkit.PromptSession") as mock_session:
            # Set up mock session
            mock_session.return_value.prompt_async.side_effect = ["echo hello", "exit"]

            # Initialize terminal
            terminal = TerminalInterface(predictor, feedback)
            terminal.session = mock_session.return_value

            # Mock command execution
            with patch.object(terminal, "_execute_command") as mock_execute:
                mock_execute.return_value = ("hello\n", 0.1)

                # Run the terminal
                await terminal.run_async()

                # Verify command was executed and saved
                mock_execute.assert_called_once_with("echo hello")
                assert "echo hello" in predictor.commands

    def test_cli_script(self):
        """Test the command-line interface script."""

        # This test would run the actual script as a subprocess
        # and verify its behavior. In a real test environment, you would:
        # 1. Start the script as a subprocess
        # 2. Send it commands via stdin
        # 3. Verify the output and behavior

        # For now, we'll just verify the script exists and is executable
        script_path = PROJECT_ROOT / "smart_terminal" / "main.py"
        assert script_path.exists()

        # Test basic help output
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"], capture_output=True, text=True
        )
        assert "usage:" in result.stdout.lower()

    def test_error_handling(self):
        """Test error handling in the application."""
        # Test with invalid command file path - should create empty commands dict
        predictor = CommandPredictor("/invalid/path/commands.json")
        assert predictor.commands == {}  # Should be empty, not raise exception

        # Test with invalid feedback file path - should create empty feedback
        feedback = FeedbackHandler("/invalid/path/feedback.json")
        assert feedback.feedback == {
            "suggestions": [],
            "ratings": [],
        }  # Should be empty, not raise exception

        # Test with invalid preset - should return default
        preset = TerminalPreset.get_preset("invalid_preset")
        assert (
            preset == TerminalPreset.DEVELOPER
        )  # Should return default, not raise exception

    def test_preset_functionality(self):
        """Test terminal presets functionality."""
        # Initialize components
        predictor = CommandPredictor(str(self.commands_file))
        feedback = FeedbackHandler(str(self.feedback_file))

        # Test each preset
        presets = [
            (TerminalPreset.DEVELOPER, "SMART", True, True, "monokai"),
            (TerminalPreset.WRITER, "FUZZY", False, False, "solarized-light"),
            (TerminalPreset.ADMIN, "EXACT", True, True, "vim"),
            (TerminalPreset.DATA_SCIENCE, "SMART", True, True, "solarized-dark"),
        ]

        for preset, mode, show_stats, auto_complete, scheme in presets:
            terminal = TerminalInterface(predictor, feedback)
            terminal.apply_preset(preset)

            assert terminal.suggestion_mode.name == mode
            assert terminal.show_typing_stats == show_stats
            assert terminal.auto_complete == auto_complete
            assert terminal.color_scheme == scheme


if __name__ == "__main__":
    pytest.main([__file__])
