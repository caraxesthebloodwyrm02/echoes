"""Unit tests for FeedbackHandler class."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from smart_terminal.core.feedback import FeedbackHandler


class TestFeedbackHandler(unittest.TestCase):
    """Test cases for FeedbackHandler class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "feedback.json"
        self.feedback = FeedbackHandler(str(self.data_file))

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test feedback handler initialization."""
        self.assertEqual(self.feedback.data_path, str(self.data_file))
        self.assertEqual(self.feedback.feedback, {"suggestions": [], "ratings": []})

    def test_load_feedback_existing_file(self):
        """Test loading feedback from an existing file."""
        test_data = {
            "suggestions": [
                {"suggestion": "test", "accepted": True, "timestamp": "2023-01-01"}
            ],
            "ratings": [{"command": "ls", "rating": 5, "timestamp": "2023-01-01"}],
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        feedback = FeedbackHandler(str(self.data_file))
        self.assertEqual(feedback.feedback, test_data)

    def test_load_feedback_nonexistent_file(self):
        """Test loading feedback when file doesn't exist."""
        non_existent = Path(self.temp_dir.name) / "nonexistent.json"
        feedback = FeedbackHandler(str(non_existent))
        self.assertEqual(feedback.feedback, {"suggestions": [], "ratings": []})

    def test_add_suggestion(self):
        """Test adding a suggestion."""
        self.feedback.add_suggestion("test suggestion", True)

        self.assertEqual(len(self.feedback.feedback["suggestions"]), 1)
        self.assertEqual(
            self.feedback.feedback["suggestions"][0]["suggestion"], "test suggestion"
        )
        self.assertTrue(self.feedback.feedback["suggestions"][0]["accepted"])
        self.assertIn("timestamp", self.feedback.feedback["suggestions"][0])

    def test_add_rating(self):
        """Test adding a command rating."""
        self.feedback.add_rating("git status", 5)

        self.assertEqual(len(self.feedback.feedback["ratings"]), 1)
        self.assertEqual(self.feedback.feedback["ratings"][0]["command"], "git status")
        self.assertEqual(self.feedback.feedback["ratings"][0]["rating"], 5)
        self.assertIn("timestamp", self.feedback.feedback["ratings"][0])

    def test_rating_bounds(self):
        """Test rating bounds enforcement."""
        # Test below minimum
        self.feedback.add_rating("cmd1", -5)
        self.assertEqual(self.feedback.feedback["ratings"][0]["rating"], 1)

        # Test above maximum
        self.feedback.add_rating("cmd2", 10)
        self.assertEqual(self.feedback.feedback["ratings"][1]["rating"], 5)

    def test_save_feedback(self):
        """Test saving feedback to file."""
        self.feedback.add_suggestion("test", True)
        self.feedback.add_rating("ls", 5)
        self.feedback.save_feedback()

        self.assertTrue(self.data_file.exists())
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data["suggestions"]), 1)
            self.assertEqual(len(data["ratings"]), 1)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_save_feedback_permission_error(self, mock_file):
        """Test handling of permission errors when saving feedback."""
        # Should not raise an exception
        self.feedback.add_suggestion("test", True)
        self.feedback.save_feedback()

    @patch("builtins.open", side_effect=IOError("Disk full"))
    def test_save_feedback_io_error(self, mock_file):
        """Test handling of IO errors when saving feedback."""
        # Should not raise an exception
        self.feedback.add_suggestion("test", True)
        self.feedback.save_feedback()


if __name__ == "__main__":
    unittest.main()
