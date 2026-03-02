"""
Models for the Echoes Agent System.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ModelSettings:
    """Settings for the language model."""

    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    name: str
    instructions: str
    model: str = "gpt-4"
    model_settings: ModelSettings = field(default_factory=ModelSettings)


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ConversationHistory:
    """History of a conversation with an agent."""

    agent_name: str
    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        """Add a message to the history."""
        self.messages.append(Message(role=role, content=content))

    def get_messages_for_api(self) -> list[dict[str, str]]:
        """Get messages in the format expected by the OpenAI API."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
