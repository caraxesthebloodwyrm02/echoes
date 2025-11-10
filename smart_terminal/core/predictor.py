# smart_terminal/core/predictor.py
import difflib
import json
import os
from datetime import datetime
from typing import Any, Dict, List


class CommandPredictor:
    def __init__(self, data_path: str = "data/commands.json"):
        self.data_path = data_path
        self.commands = self._load_commands()
        self.context: List[Dict[str, Any]] = []
        self.max_history = 10

    def _load_commands(self) -> Dict[str, int]:
        """Load command frequencies from file"""
        try:
            if os.path.exists(self.data_path) and os.path.getsize(self.data_path) > 0:
                with open(self.data_path, "r") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load command data: {e}")
        return {}

    def save_commands(self):
        """Save command frequencies to file"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(self.commands, f, indent=2)

    def update_command(self, command: str):
        """Update command frequency and context"""
        if not command.strip():
            return

        self.commands[command] = self.commands.get(command, 0) + 1
        self.context.append(
            {"command": command, "timestamp": datetime.now().isoformat()}
        )
        self.context = self.context[-self.max_history :]
        self.save_commands()

    def get_suggestions(self, text: str) -> List[str]:
        """Get command suggestions based on input"""
        if not text.strip():
            return []

        # Simple prefix matching
        matches = [cmd for cmd in self.commands if cmd.startswith(text)]

        # Sort by frequency (most used first)
        return sorted(matches, key=lambda x: self.commands[x], reverse=True)[:5]

    def get_context_aware_suggestions(self, text: str) -> List[str]:
        """Get suggestions based on current context and input"""
        if not text.strip():
            return []

        # Get basic command suggestions
        command_suggestions = self.get_suggestions(text)

        # Add contextual suggestions based on recent commands
        recent_commands = [c["command"] for c in self.context[-3:]]
        if recent_commands:
            last_command = recent_commands[-1].lower()

            # Git context
            if "git" in last_command:
                git_commands = [
                    "status",
                    "add",
                    'commit -m "',
                    "push",
                    "pull",
                    "checkout",
                    "branch",
                ]
                command_suggestions.extend(
                    [
                        f"git {cmd}"
                        for cmd in git_commands
                        if f"git {cmd}" not in " ".join(command_suggestions)
                    ][:3]
                )

            # Python context
            elif "python" in last_command or "pip" in last_command:
                python_commands = [
                    "python -m pip install",
                    "python -m pytest",
                    "python -m venv venv",
                ]
                command_suggestions.extend(
                    [cmd for cmd in python_commands if cmd not in command_suggestions][
                        :2
                    ]
                )

        # Use fuzzy matching for better suggestions
        all_commands = list(set(self.commands.keys()))
        fuzzy_matches = difflib.get_close_matches(text, all_commands, n=3, cutoff=0.4)

        # Combine and deduplicate
        combined = list(dict.fromkeys(command_suggestions + fuzzy_matches))

        return combined[:5]  # Return top 5 suggestions
