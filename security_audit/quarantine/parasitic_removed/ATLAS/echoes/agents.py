"""
Echoes AI Agent System

This module provides agent management functionality for the Echoes AI Multi-Agent System.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .config import Settings
from .exceptions import AgentError, ValidationError

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Agent configuration model."""

    name: str = Field(..., description="Agent name")
    description: str | None = Field(None, description="Agent description")
    system_prompt: str | None = Field(None, description="System prompt for the agent")
    temperature: float = Field(
        0.7, description="Temperature for AI responses", ge=0.0, le=2.0
    )
    max_tokens: int = Field(1000, description="Maximum tokens for responses", gt=0)
    model: str = Field("gpt-3.5-turbo", description="AI model to use")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Message(BaseModel):
    """Message model for agent conversations."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    token_count: int | None = Field(None, description="Token count for the message")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Conversation(BaseModel):
    """Conversation model for agent interactions."""

    id: str = Field(..., description="Conversation ID")
    agent_id: str = Field(..., description="Agent ID")
    user_id: str = Field(..., description="User ID")
    title: str | None = Field(None, description="Conversation title")
    messages: list[Message] = Field(
        default_factory=list, description="Conversation messages"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = Field("active", description="Conversation status")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Agent(BaseModel):
    """Agent model for AI assistant management."""

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    description: str | None = Field(None, description="Agent description")
    user_id: str = Field(..., description="User ID who owns the agent")
    config: AgentConfig = Field(..., description="Agent configuration")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = Field(True, description="Whether the agent is active")
    conversation_count: int = Field(0, description="Number of conversations")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AgentManager:
    """Manager for agent operations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.agents: dict[str, Agent] = {}
        self.conversations: dict[str, Conversation] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize the agent manager."""
        if self._initialized:
            return

        logger.info("Initializing AgentManager...")

        # Load agents from storage (in production, this would be from database)
        await self._load_agents()

        self._initialized = True
        logger.info("AgentManager initialized successfully")

    async def cleanup(self):
        """Cleanup the agent manager."""
        if not self._initialized:
            return

        logger.info("Cleaning up AgentManager...")

        # Save agents to storage
        await self._save_agents()

        self._initialized = False
        logger.info("AgentManager cleaned up successfully")

    async def create_agent(self, user_id: str, config: AgentConfig) -> Agent:
        """Create a new agent."""
        # Validate configuration
        if not config.name.strip():
            raise ValidationError("Agent name cannot be empty")

        # Check if user has reached agent limit
        user_agents = [a for a in self.agents.values() if a.user_id == user_id]
        if len(user_agents) >= self.settings.max_agents_per_user:
            raise AgentError(
                f"User has reached maximum agent limit of {self.settings.max_agents_per_user}",
                details={"user_id": user_id},
            )

        # Create agent
        agent_id = f"agent_{len(self.agents) + 1}"
        agent = Agent(
            id=agent_id,
            name=config.name,
            description=config.description,
            user_id=user_id,
            config=config,
        )

        # Store agent
        self.agents[agent_id] = agent

        logger.info(f"Created agent {agent_id} for user {user_id}")
        return agent

    async def get_agent(self, agent_id: str) -> Agent | None:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    async def update_agent(self, agent_id: str, config: AgentConfig) -> Agent:
        """Update an agent's configuration."""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise AgentError(f"Agent not found: {agent_id}", agent_id=agent_id)

        # Update agent
        agent.config = config
        agent.updated_at = datetime.now(UTC)

        logger.info(f"Updated agent {agent_id}")
        return agent

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        if agent_id not in self.agents:
            raise AgentError(f"Agent not found: {agent_id}", agent_id=agent_id)

        # Delete agent and its conversations
        del self.agents[agent_id]

        # Remove conversations for this agent
        conversations_to_delete = [
            conv_id
            for conv_id, conv in self.conversations.items()
            if conv.agent_id == agent_id
        ]
        for conv_id in conversations_to_delete:
            del self.conversations[conv_id]

        logger.info(f"Deleted agent {agent_id}")
        return True

    async def list_agents(self, user_id: str | None = None) -> list[Agent]:
        """List agents, optionally filtered by user."""
        agents = list(self.agents.values())
        if user_id:
            agents = [a for a in agents if a.user_id == user_id]
        return agents

    async def create_conversation(
        self, agent_id: str, user_id: str, title: str | None = None
    ) -> Conversation:
        """Create a new conversation."""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise AgentError(f"Agent not found: {agent_id}", agent_id=agent_id)

        if agent.user_id != user_id:
            raise AgentError("Agent does not belong to user", agent_id=agent_id)

        # Check conversation limit
        agent_conversations = [
            c
            for c in self.conversations.values()
            if c.agent_id == agent_id and c.status == "active"
        ]
        if len(agent_conversations) >= self.settings.max_conversations_per_agent:
            raise AgentError(
                f"Agent has reached maximum conversation limit of {self.settings.max_conversations_per_agent}",
                agent_id=agent_id,
            )

        # Create conversation
        conversation_id = f"conv_{len(self.conversations) + 1}"
        conversation = Conversation(
            id=conversation_id,
            agent_id=agent_id,
            user_id=user_id,
            title=title or f"Conversation {len(agent_conversations) + 1}",
        )

        # Store conversation
        self.conversations[conversation_id] = conversation

        # Update agent conversation count
        agent.conversation_count += 1

        logger.info(f"Created conversation {conversation_id} for agent {agent_id}")
        return conversation

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)

    async def add_message(self, conversation_id: str, message: Message) -> Conversation:
        """Add a message to a conversation."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise AgentError(f"Conversation not found: {conversation_id}")

        # Check message limit
        if len(conversation.messages) >= self.settings.conversation_history_limit:
            # Remove oldest messages if limit exceeded
            conversation.messages = conversation.messages[
                -(self.settings.conversation_history_limit - 1) :
            ]

        # Add message
        conversation.messages.append(message)
        conversation.updated_at = datetime.now(UTC)

        logger.info(f"Added message to conversation {conversation_id}")
        return conversation

    async def get_conversation_history(
        self, conversation_id: str, limit: int | None = None
    ) -> list[Message]:
        """Get conversation history."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise AgentError(f"Conversation not found: {conversation_id}")

        messages = conversation.messages
        if limit:
            messages = messages[-limit:]

        return messages

    async def reset_conversation(self, conversation_id: str) -> Conversation:
        """Reset a conversation by clearing its messages."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise AgentError(f"Conversation not found: {conversation_id}")

        conversation.messages = []
        conversation.updated_at = datetime.now(UTC)

        logger.info(f"Reset conversation {conversation_id}")
        return conversation

    async def _load_agents(self):
        """Load agents from storage (placeholder)."""
        # In production, this would load from database
        pass

    async def _save_agents(self):
        """Save agents to storage (placeholder)."""
        # In production, this would save to database
        pass


# Global agent manager instance
_agent_manager: AgentManager | None = None


def get_agent_manager() -> AgentManager:
    """Get the global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager(get_settings())
    return _agent_manager


async def initialize_agent_manager():
    """Initialize the global agent manager."""
    manager = get_agent_manager()
    await manager.initialize()


async def cleanup_agent_manager():
    """Cleanup the global agent manager."""
    manager = get_agent_manager()
    await manager.cleanup()
