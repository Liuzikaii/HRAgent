"""Pydantic schemas for chat API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request body for sending a chat message."""
    message: str
    session_id: Optional[UUID] = None


class ChatMessageResponse(BaseModel):
    """A single chat message in the response."""
    id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    session_id: UUID
    message: ChatMessageResponse


class ChatSessionResponse(BaseModel):
    """A chat session summary."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    """List of chat sessions."""
    sessions: list[ChatSessionResponse]


class ChatHistoryResponse(BaseModel):
    """Full chat history for a session."""
    session_id: UUID
    messages: list[ChatMessageResponse]
