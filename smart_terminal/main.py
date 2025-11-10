# smart_terminal/main.py
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from smart_terminal.core.feedback import FeedbackHandler
# Now import local modules
from smart_terminal.core.predictor import CommandPredictor
from smart_terminal.interface.terminal import TerminalInterface


def setup_environment():
    """Set up required directories and files"""
    os.makedirs("data", exist_ok=True)


def main():
    """Main entry point for the smart terminal"""
    try:
        setup_environment()

        # Initialize components
        predictor = CommandPredictor()
        feedback = FeedbackHandler()
        terminal = TerminalInterface(predictor, feedback)

        # Start the terminal
        terminal.run()

    except KeyboardInterrupt:
        print("\nExiting gracefully...")
    except Exception as e:
        print(f"\nFatal error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
