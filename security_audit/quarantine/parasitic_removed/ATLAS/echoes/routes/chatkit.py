"""
Echoes AI ChatKit Routes

This module provides ChatKit integration endpoints for the Echoes AI Multi-Agent System.
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..exceptions import create_success_response

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Create ChatKit session request model."""

    user_id: str = Field(..., description="User ID")
    agent_id: str | None = Field(None, description="Agent ID to associate with session")
    workflow_id: str | None = Field(
        None, description="Workflow ID to associate with session"
    )
    title: str | None = Field(None, description="Session title")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ChatKitSession(BaseModel):
    """ChatKit session model."""

    id: str
    user_id: str
    agent_id: str | None
    workflow_id: str | None
    title: str | None
    created_at: datetime
    updated_at: datetime
    status: str
    metadata: dict[str, Any]


class SessionResponse(BaseModel):
    """ChatKit session response model."""

    id: str
    user_id: str
    agent_id: str | None
    workflow_id: str | None
    title: str | None
    created_at: str
    updated_at: str
    status: str
    metadata: dict[str, Any]
    embed_url: str
    api_url: str


# In-memory session storage (in production, this would be in a database)
sessions: dict[str, ChatKitSession] = {}


@router.post("/session", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new ChatKit session."""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())

        # Create session
        now = datetime.now(UTC)
        session = ChatKitSession(
            id=session_id,
            user_id=request.user_id,
            agent_id=request.agent_id,
            workflow_id=request.workflow_id,
            title=request.title or f"Chat Session {len(sessions) + 1}",
            created_at=now,
            updated_at=now,
            status="active",
            metadata=request.metadata,
        )

        # Store session
        sessions[session_id] = session

        # Create response
        response = SessionResponse(
            id=session.id,
            user_id=session.user_id,
            agent_id=session.agent_id,
            workflow_id=session.workflow_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            status=session.status,
            metadata=session.metadata,
            embed_url=f"https://chat.echoes.ai/embed/{session_id}",
            api_url=f"https://api.echoes.ai/chatkit/{session_id}",
        )

        logger.info(f"Created ChatKit session {session_id} for user {request.user_id}")
        return response

    except Exception as e:
        logger.error(f"Failed to create ChatKit session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get a ChatKit session by ID."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        response = SessionResponse(
            id=session.id,
            user_id=session.user_id,
            agent_id=session.agent_id,
            workflow_id=session.workflow_id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            status=session.status,
            metadata=session.metadata,
            embed_url=f"https://chat.echoes.ai/embed/{session_id}",
            api_url=f"https://api.echoes.ai/chatkit/{session_id}",
        )

        logger.info(f"Retrieved ChatKit session {session_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ChatKit session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/session/{session_id}")
async def update_session(
    session_id: str,
    title: str | None = None,
    status: str | None = None,
    metadata: dict[str, Any] = None,
):
    """Update a ChatKit session."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        # Update session
        if title is not None:
            session.title = title
        if status is not None:
            session.status = status
        if metadata is not None:
            session.metadata.update(metadata)

        session.updated_at = datetime.now(UTC)

        logger.info(f"Updated ChatKit session {session_id}")
        return create_success_response(
            data={"session_id": session_id}, message="Session updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update ChatKit session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a ChatKit session."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        del sessions[session_id]

        logger.info(f"Deleted ChatKit session {session_id}")
        return create_success_response(data={}, message="Session deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete ChatKit session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions")
async def list_sessions(user_id: str | None = None):
    """List ChatKit sessions, optionally filtered by user."""
    try:
        session_list = list(sessions.values())

        if user_id:
            session_list = [s for s in session_list if s.user_id == user_id]

        # Convert to response format
        responses = []
        for session in session_list:
            response = SessionResponse(
                id=session.id,
                user_id=session.user_id,
                agent_id=session.agent_id,
                workflow_id=session.workflow_id,
                title=session.title,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                status=session.status,
                metadata=session.metadata,
                embed_url=f"https://chat.echoes.ai/embed/{session.id}",
                api_url=f"https://api.echoes.ai/chatkit/{session.id}",
            )
            responses.append(response)

        logger.info(f"Listed {len(responses)} ChatKit sessions")
        return responses

    except Exception as e:
        logger.error(f"Failed to list ChatKit sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}/embed")
async def get_embed_code(session_id: str):
    """Get embed code for a ChatKit session."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        embed_code = f"""
<iframe
    src="https://chat.echoes.ai/embed/{session_id}"
    width="100%"
    height="600"
    frameborder="0"
    style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
></iframe>
        """.strip()

        response = {
            "session_id": session_id,
            "embed_url": f"https://chat.echoes.ai/embed/{session_id}",
            "embed_code": embed_code,
            "api_url": f"https://api.echoes.ai/chatkit/{session_id}",
            "title": session.title,
        }

        logger.info(f"Generated embed code for ChatKit session {session_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get embed code for ChatKit session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/session/{session_id}/message")
async def send_message(session_id: str, message: str, role: str = "user"):
    """Send a message to a ChatKit session."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        session.updated_at = datetime.now(UTC)

        # In production, this would integrate with the agent system
        # For now, we'll simulate a response

        response = {
            "session_id": session_id,
            "message": {
                "role": role,
                "content": message,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "response": {
                "role": "assistant",
                "content": f"I received your message: '{message}'. This is a simulated response from the Echoes AI system.",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        logger.info(f"Sent message to ChatKit session {session_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message to ChatKit session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}/config")
async def get_session_config(session_id: str):
    """Get configuration for a ChatKit session."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        config = {
            "session_id": session_id,
            "user_id": session.user_id,
            "agent_id": session.agent_id,
            "workflow_id": session.workflow_id,
            "title": session.title,
            "theme": "light",
            "colors": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "background": "#ffffff",
                "text": "#333333",
            },
            "features": {
                "file_upload": True,
                "voice_input": False,
                "markdown_support": True,
                "code_highlighting": True,
                "emoji_support": True,
            },
            "limits": {
                "max_message_length": 4000,
                "max_file_size": 10485760,  # 10MB
                "rate_limit": 60,  # requests per minute
            },
        }

        logger.info(f"Retrieved config for ChatKit session {session_id}")
        return config

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get config for ChatKit session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats")
async def get_chatkit_stats():
    """Get ChatKit usage statistics."""
    try:
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions.values() if s.status == "active"])

        # Group by user
        user_sessions = {}
        for session in sessions.values():
            if session.user_id not in user_sessions:
                user_sessions[session.user_id] = 0
            user_sessions[session.user_id] += 1

        stats = {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "inactive_sessions": total_sessions - active_sessions,
            "unique_users": len(user_sessions),
            "average_sessions_per_user": total_sessions / len(user_sessions)
            if user_sessions
            else 0,
            "top_users": sorted(
                user_sessions.items(), key=lambda x: x[1], reverse=True
            )[:10],
        }

        logger.info("Retrieved ChatKit statistics")
        return stats

    except Exception as e:
        logger.error(f"Failed to get ChatKit statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
