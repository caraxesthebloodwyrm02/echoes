"""Pytest configuration and fixtures."""

import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is in sys.path for IDE runs
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from smart_terminal.core.feedback import FeedbackHandler
from smart_terminal.core.predictor import CommandPredictor
from smart_terminal.interface.terminal import TerminalInterface


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="function")
def predictor(temp_dir: Path) -> CommandPredictor:
    """Create a CommandPredictor instance with a temporary data file."""
    commands_file = temp_dir / "commands.json"
    return CommandPredictor(str(commands_file))


@pytest.fixture(scope="function")
def feedback(temp_dir: Path) -> FeedbackHandler:
    """Create a FeedbackHandler instance with a temporary data file."""
    feedback_file = temp_dir / "feedback.json"
    return FeedbackHandler(str(feedback_file))


@pytest.fixture(scope="function")
def terminal(
    predictor: CommandPredictor, feedback: FeedbackHandler
) -> TerminalInterface:
    """Create a TerminalInterface instance with mocked dependencies."""
    # Mock the prompt toolkit imports
    with patch("prompt_toolkit.PromptSession"):
        term = TerminalInterface(predictor, feedback)
        term.session = MagicMock()
        term.session.prompt = MagicMock(return_value="exit")
        term.session.prompt_async = AsyncMock(return_value="exit")
        return term


@pytest.fixture(scope="function")
def async_runner():
    """Run async test functions."""

    def _run(coro):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    return _run


# Async mock for Python 3.7+
class AsyncMock(MagicMock):
    """Async mock for testing async functions."""

    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
