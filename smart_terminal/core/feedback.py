import json
import os
from datetime import datetime
from typing import Dict


class FeedbackHandler:
    def __init__(self, data_path: str = "data/feedback.json"):
        self.data_path = data_path
        self.feedback = self._load_feedback()

    def _load_feedback(self) -> Dict[str, list[dict]]:
        """Load feedback data from file"""
        try:
            if os.path.exists(self.data_path) and os.path.getsize(self.data_path) > 0:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load feedback data ({e}), starting fresh")
        return {"suggestions": [], "ratings": []}

    def save_feedback(self):
        """Save feedback to file"""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.feedback, f, indent=2)
        except (OSError, PermissionError, IOError):
            # Silently fail for file system errors - don't let feedback break the app
            pass

    def add_suggestion(self, suggestion: str, accepted: bool):
        """Add a suggestion feedback"""
        self.feedback["suggestions"].append(
            {
                "suggestion": suggestion,
                "accepted": accepted,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.save_feedback()

    def add_rating(self, command: str, rating: int):
        """Add a command rating (1-5)"""
        self.feedback["ratings"].append(
            {
                "command": command,
                "rating": max(1, min(5, rating)),
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.save_feedback()
