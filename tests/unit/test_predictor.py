"""Unit tests for CommandPredictor class."""
import json
import tempfile
import unittest
from pathlib import Path

from smart_terminal.core.predictor import CommandPredictor


class TestCommandPredictor(unittest.TestCase):
    """Test cases for CommandPredictor class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "commands.json"
        self.predictor = CommandPredictor(str(self.data_file))

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test predictor initialization."""
        self.assertEqual(self.predictor.data_path, str(self.data_file))
        self.assertEqual(self.predictor.commands, {})
        self.assertEqual(len(self.predictor.context), 0)

    def test_load_commands_existing_file(self):
        """Test loading commands from an existing file."""
        test_commands = {"git status": 5, "ls -la": 3}
        with open(self.data_file, "w") as f:
            f.write('{"git status": 5, "ls -la": 3}')

        predictor = CommandPredictor(str(self.data_file))
        self.assertEqual(predictor.commands, test_commands)

    def test_load_commands_nonexistent_file(self):
        """Test loading commands when file doesn't exist."""
        non_existent = Path(self.temp_dir.name) / "nonexistent.json"
        predictor = CommandPredictor(str(non_existent))
        self.assertEqual(predictor.commands, {})

    def test_update_command(self):
        """Test updating command frequency."""
        self.predictor.update_command("git status")
        self.assertEqual(self.predictor.commands["git status"], 1)

        # Update same command again
        self.predictor.update_command("git status")
        self.assertEqual(self.predictor.commands["git status"], 2)

    def test_save_commands(self):
        """Test saving commands to file."""
        self.predictor.update_command("git status")
        self.predictor.update_command("ls -la")
        self.predictor.save_commands()

        self.assertTrue(self.data_file.exists())
        with open(self.data_file, "r") as f:
            data = json.load(f)
            self.assertEqual(data, {"git status": 1, "ls -la": 1})

    def test_get_suggestions_empty(self):
        """Test getting suggestions with empty input."""
        suggestions = self.predictor.get_suggestions("")
        self.assertEqual(suggestions, [])

    def test_get_suggestions_no_matches(self):
        """Test getting suggestions with no matches."""
        self.predictor.update_command("git status")
        suggestions = self.predictor.get_suggestions("python")
        self.assertEqual(suggestions, [])

    def test_get_suggestions_with_matches(self):
        """Test getting suggestions with matching commands."""
        self.predictor.update_command("git status")
        self.predictor.update_command("git add .")
        self.predictor.update_command("ls -la")

        suggestions = self.predictor.get_suggestions("git")
        self.assertEqual(set(suggestions), {"git status", "git add ."})

    def test_context_tracking(self):
        """Test command context tracking."""
        self.predictor.update_command("git status")
        self.predictor.update_command("ls -la")

        self.assertEqual(len(self.predictor.context), 2)
        self.assertEqual(self.predictor.context[0]["command"], "git status")
        self.assertEqual(self.predictor.context[1]["command"], "ls -la")

    def test_context_limits(self):
        """Test context history limit."""
        for i in range(15):  # More than max_history (default 10)
            self.predictor.update_command(f"command_{i}")

        self.assertEqual(
            len(self.predictor.context), 10
        )  # Should be limited to max_history
        self.assertEqual(
            self.predictor.context[0]["command"], "command_5"
        )  # First 5 should be discarded


if __name__ == "__main__":
    unittest.main()
