"""
Echoes AI Agent Routes

This module provides agent-related endpoints for the Echoes AI Multi-Agent System.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..agents import AgentConfig, get_agent_manager
from ..exceptions import AgentError, ValidationError, create_success_response

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateAgentRequest(BaseModel):
    """Create agent request model."""

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


class UpdateAgentRequest(BaseModel):
    """Update agent request model."""

    name: str | None = Field(None, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    system_prompt: str | None = Field(None, description="System prompt for the agent")
    temperature: float | None = Field(
        None, description="Temperature for AI responses", ge=0.0, le=2.0
    )
    max_tokens: int | None = Field(
        None, description="Maximum tokens for responses", gt=0
    )
    model: str | None = Field(None, description="AI model to use")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class CreateConversationRequest(BaseModel):
    """Create conversation request model."""

    title: str | None = Field(None, description="Conversation title")


class AddMessageRequest(BaseModel):
    """Add message request model."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AgentResponse(BaseModel):
    """Agent response model."""

    id: str
    name: str
    description: str | None
    user_id: str
    config: AgentConfig
    created_at: str
    updated_at: str
    is_active: bool
    conversation_count: int
    metadata: dict[str, Any]


class ConversationResponse(BaseModel):
    """Conversation response model."""

    id: str
    agent_id: str
    user_id: str
    title: str | None
    message_count: int
    created_at: str
    updated_at: str
    status: str
    metadata: dict[str, Any]


class MessageResponse(BaseModel):
    """Message response model."""

    role: str
    content: str
    timestamp: str
    token_count: int | None
    metadata: dict[str, Any]


@router.post("/create", response_model=AgentResponse)
async def create_agent(
    request: CreateAgentRequest, user_id: str = Query(..., description="User ID")
):
    """Create a new agent."""
    try:
        agent_manager = get_agent_manager()

        config = AgentConfig(
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model=request.model,
            metadata=request.metadata,
        )

        agent = await agent_manager.create_agent(user_id, config)

        response = AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            user_id=agent.user_id,
            config=agent.config,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat(),
            is_active=agent.is_active,
            conversation_count=agent.conversation_count,
            metadata=agent.metadata,
        )

        logger.info(f"Created agent {agent.id} for user {user_id}")
        return response

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except AgentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list", response_model=list[AgentResponse])
async def list_agents(
    user_id: str | None = Query(None, description="Filter by user ID")
):
    """List agents."""
    try:
        agent_manager = get_agent_manager()
        agents = await agent_manager.list_agents(user_id)

        responses = []
        for agent in agents:
            response = AgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                user_id=agent.user_id,
                config=agent.config,
                created_at=agent.created_at.isoformat(),
                updated_at=agent.updated_at.isoformat(),
                is_active=agent.is_active,
                conversation_count=agent.conversation_count,
                metadata=agent.metadata,
            )
            responses.append(response)

        logger.info(f"Listed {len(responses)} agents")
        return responses

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get an agent by ID."""
    try:
        agent_manager = get_agent_manager()
        agent = await agent_manager.get_agent(agent_id)

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        response = AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            user_id=agent.user_id,
            config=agent.config,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat(),
            is_active=agent.is_active,
            conversation_count=agent.conversation_count,
            metadata=agent.metadata,
        )

        logger.info(f"Retrieved agent {agent_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    request: UpdateAgentRequest,
    user_id: str = Query(..., description="User ID"),
):
    """Update an agent."""
    try:
        agent_manager = get_agent_manager()

        # Get existing agent
        existing_agent = await agent_manager.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if existing_agent.user_id != user_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to user")

        # Create updated config
        config = AgentConfig(
            name=request.name
            if request.name is not None
            else existing_agent.config.name,
            description=request.description
            if request.description is not None
            else existing_agent.config.description,
            system_prompt=request.system_prompt
            if request.system_prompt is not None
            else existing_agent.config.system_prompt,
            temperature=request.temperature
            if request.temperature is not None
            else existing_agent.config.temperature,
            max_tokens=request.max_tokens
            if request.max_tokens is not None
            else existing_agent.config.max_tokens,
            model=request.model
            if request.model is not None
            else existing_agent.config.model,
            metadata=request.metadata
            if request.metadata
            else existing_agent.config.metadata,
        )

        agent = await agent_manager.update_agent(agent_id, config)

        response = AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            user_id=agent.user_id,
            config=agent.config,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat(),
            is_active=agent.is_active,
            conversation_count=agent.conversation_count,
            metadata=agent.metadata,
        )

        logger.info(f"Updated agent {agent_id}")
        return response

    except HTTPException:
        raise
    except AgentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, user_id: str = Query(..., description="User ID")):
    """Delete an agent."""
    try:
        agent_manager = get_agent_manager()

        # Get existing agent
        existing_agent = await agent_manager.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if existing_agent.user_id != user_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to user")

        await agent_manager.delete_agent(agent_id)

        logger.info(f"Deleted agent {agent_id}")
        return create_success_response(data={}, message="Agent deleted successfully")

    except HTTPException:
        raise
    except AgentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{agent_id}/conversations/create", response_model=ConversationResponse)
async def create_conversation(
    agent_id: str,
    request: CreateConversationRequest,
    user_id: str = Query(..., description="User ID"),
):
    """Create a new conversation for an agent."""
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists and belongs to user
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if agent.user_id != user_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to user")

        conversation = await agent_manager.create_conversation(
            agent_id, user_id, request.title
        )

        response = ConversationResponse(
            id=conversation.id,
            agent_id=conversation.agent_id,
            user_id=conversation.user_id,
            title=conversation.title,
            message_count=len(conversation.messages),
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            status=conversation.status,
            metadata=conversation.metadata,
        )

        logger.info(f"Created conversation {conversation.id} for agent {agent_id}")
        return response

    except HTTPException:
        raise
    except AgentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{agent_id}/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    agent_id: str, user_id: str = Query(..., description="User ID")
):
    """List conversations for an agent."""
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists and belongs to user
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if agent.user_id != user_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to user")

        # Get all conversations and filter by agent
        all_conversations = list(agent_manager.conversations.values())
        agent_conversations = [
            conv
            for conv in all_conversations
            if conv.agent_id == agent_id and conv.user_id == user_id
        ]

        responses = []
        for conversation in agent_conversations:
            response = ConversationResponse(
                id=conversation.id,
                agent_id=conversation.agent_id,
                user_id=conversation.user_id,
                title=conversation.title,
                message_count=len(conversation.messages),
                created_at=conversation.created_at.isoformat(),
                updated_at=conversation.updated_at.isoformat(),
                status=conversation.status,
                metadata=conversation.metadata,
            )
            responses.append(response)

        logger.info(f"Listed {len(responses)} conversations for agent {agent_id}")
        return responses

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{agent_id}/conversations/{conversation_id}/history",
    response_model=list[MessageResponse],
)
async def get_conversation_history(
    agent_id: str,
    conversation_id: str,
    user_id: str = Query(..., description="User ID"),
    limit: int | None = Query(None, description="Limit number of messages"),
):
    """Get conversation history."""
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists and belongs to user
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if agent.user_id != user_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to user")

        # Get conversation
        conversation = await agent_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Conversation does not belong to user"
            )

        messages = await agent_manager.get_conversation_history(conversation_id, limit)

        responses = []
        for message in messages:
            response = MessageResponse(
                role=message.role,
                content=message.content,
                timestamp=message.timestamp.isoformat(),
                token_count=message.token_count,
                metadata=message.metadata,
            )
            responses.append(response)

        logger.info(
            f"Retrieved {len(responses)} messages for conversation {conversation_id}"
        )
        return responses

    except HTTPException:
        raise
    except AgentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{agent_id}/conversations/{conversation_id}/reset")
async def reset_conversation(
    agent_id: str,
    conversation_id: str,
    user_id: str = Query(..., description="User ID"),
):
    """Reset a conversation by clearing its messages."""
    try:
        agent_manager = get_agent_manager()

        # Verify agent exists and belongs to user
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if agent.user_id != user_id:
            raise HTTPException(status_code=403, detail="Agent does not belong to user")

        # Get and verify conversation
        conversation = await agent_manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Conversation does not belong to user"
            )

        await agent_manager.reset_conversation(conversation_id)

        logger.info(f"Reset conversation {conversation_id}")
        return create_success_response(
            data={}, message="Conversation reset successfully"
        )

    except HTTPException:
        raise
    except AgentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to reset conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
