"""
Context Manager for Echoes Assistant
Manages conversation context and state transitions
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Represents the current conversation context"""

    session_id: str
    current_topic: str = ""
    context_depth: int = 0
    entities: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ContextManager:
    """
    Manages conversation context and state transitions for the Echoes assistant.
    Provides context-aware conversation flow and state management.
    """

    def __init__(self):
        self.contexts: dict[str, ConversationContext] = {}
        self.logger = logging.getLogger(__name__)

    def get_context(self, session_id: str) -> ConversationContext | None:
        """
        Get the conversation context for a session

        Args:
            session_id: The session identifier

        Returns:
            ConversationContext or None if not found
        """
        return self.contexts.get(session_id)

    def create_context(
        self, session_id: str, initial_topic: str = ""
    ) -> ConversationContext:
        """
        Create a new conversation context

        Args:
            session_id: The session identifier
            initial_topic: Initial conversation topic

        Returns:
            The created ConversationContext
        """
        context = ConversationContext(
            session_id=session_id, current_topic=initial_topic
        )
        self.contexts[session_id] = context
        self.logger.debug(f"Created context for session {session_id}")
        return context

    def update_context(self, session_id: str, **updates) -> ConversationContext | None:
        """
        Update conversation context

        Args:
            session_id: The session identifier
            **updates: Key-value pairs to update

        Returns:
            Updated ConversationContext or None if not found
        """
        context = self.get_context(session_id)
        if context:
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            context.updated_at = datetime.now()
            self.logger.debug(f"Updated context for session {session_id}: {updates}")
        return context

    def clear_context(self, session_id: str) -> bool:
        """
        Clear conversation context

        Args:
            session_id: The session identifier

        Returns:
            True if context was cleared, False if not found
        """
        if session_id in self.contexts:
            del self.contexts[session_id]
            self.logger.debug(f"Cleared context for session {session_id}")
            return True
        return False

    def add_entity(self, session_id: str, entity: dict[str, Any]) -> bool:
        """
        Add an entity to the conversation context

        Args:
            session_id: The session identifier
            entity: Entity information

        Returns:
            True if entity was added, False if context not found
        """
        context = self.get_context(session_id)
        if context:
            context.entities.append(entity)
            context.updated_at = datetime.now()
            self.logger.debug(f"Added entity to session {session_id}: {entity}")
            return True
        return False

    def get_entities(self, session_id: str) -> list[dict[str, Any]]:
        """
        Get entities from conversation context

        Args:
            session_id: The session identifier

        Returns:
            List of entities
        """
        context = self.get_context(session_id)
        return context.entities if context else []

    def get_context_summary(self, session_id: str) -> dict[str, Any]:
        """
        Get a summary of the conversation context

        Args:
            session_id: The session identifier

        Returns:
            Context summary dictionary
        """
        context = self.get_context(session_id)
        if context:
            return {
                "session_id": context.session_id,
                "current_topic": context.current_topic,
                "context_depth": context.context_depth,
                "entity_count": len(context.entities),
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
            }
        return {}

    def transition_context(self, session_id: str, new_topic: str) -> bool:
        """
        Transition to a new conversation topic

        Args:
            session_id: The session identifier
            new_topic: New conversation topic

        Returns:
            True if transition successful, False if context not found
        """
        context = self.get_context(session_id)
        if context:
            context.current_topic = new_topic
            context.context_depth += 1
            context.updated_at = datetime.now()
            self.logger.debug(
                f"Transitioned session {session_id} to topic: {new_topic}"
            )
            return True
        return False


# Global instance for easy access
context_manager = ContextManager()
