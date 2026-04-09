"""Chat API routes."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ChatSessionListResponse,
    ChatSessionResponse,
)
from app.services.agent import chat, chat_stream

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_message(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message and get an AI response."""
    # Get or create session
    if req.session_id:
        session = await db.get(ChatSession, req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(title=req.message[:50])
        db.add(session)
        await db.flush()

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=req.message)
    db.add(user_msg)
    await db.flush()

    # Load chat history for context
    history_query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(history_query)
    history_messages = result.scalars().all()
    chat_history = [{"role": m.role, "content": m.content} for m in history_messages[:-1]]

    # Get AI response
    try:
        ai_content = await chat(req.message, chat_history)
    except Exception as e:
        logger.error(f"Agent error: {e}")
        ai_content = "抱歉，系统暂时无法处理您的请求，请稍后再试。"

    # Save AI response
    ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_content)
    db.add(ai_msg)
    await db.flush()

    return ChatResponse(
        session_id=session.id,
        message=ChatMessageResponse.model_validate(ai_msg),
    )


@router.post("/stream")
async def send_message_stream(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message and stream the AI response via SSE."""
    # Get or create session
    if req.session_id:
        session = await db.get(ChatSession, req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(title=req.message[:50])
        db.add(session)
        await db.flush()

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role="user", content=req.message)
    db.add(user_msg)
    await db.flush()

    # Load chat history
    history_query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(history_query)
    history_messages = result.scalars().all()
    chat_history = [{"role": m.role, "content": m.content} for m in history_messages[:-1]]

    session_id = str(session.id)

    async def event_generator():
        full_content = []
        try:
            async for chunk in chat_stream(req.message, chat_history):
                full_content.append(chunk)
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: [ERROR] 系统暂时无法处理您的请求\n\n"

        # Save the full AI response to DB
        final_content = "".join(full_content)
        if final_content:
            async with get_db_session() as save_db:
                ai_msg = ChatMessage(
                    session_id=uuid.UUID(session_id),
                    role="assistant",
                    content=final_content,
                )
                save_db.add(ai_msg)
                await save_db.commit()

        yield f"data: [DONE]{session_id}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-Id": session_id,
        },
    )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions, most recent first."""
    query = select(ChatSession).order_by(ChatSession.updated_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()
    return ChatSessionListResponse(
        sessions=[ChatSessionResponse.model_validate(s) for s in sessions]
    )


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_session_messages(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get all messages in a specific chat session."""
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(query)
    messages = result.scalars().all()

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a chat session and all its messages."""
    session = await db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    return {"message": "Session deleted successfully"}


# Helper for saving streamed responses outside the request context
from app.database import async_session as get_db_session_maker


class get_db_session:
    """Async context manager for getting a DB session outside request scope."""

    async def __aenter__(self):
        self.session = get_db_session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
