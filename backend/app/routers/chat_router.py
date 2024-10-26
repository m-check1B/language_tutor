import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, desc
from datetime import datetime
from ..database import get_db
from ..auth import get_current_user
from ..models import ChatSession, ChatMessage, User

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

@router.get("/chat/conversations")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    try:
        query = (
            select(ChatSession)
            .where(ChatSession.user_id == current_user["id"])
            .order_by(desc(ChatSession.created_at))
        )
        result = await db.execute(query)
        sessions = result.scalars().all()

        conversations = []
        for session in sessions:
            messages_query = (
                select(ChatMessage)
                .where(ChatMessage.chat_session_id == session.id)
                .order_by(ChatMessage.created_at)
            )
            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()
            
            # Only include conversations that have messages
            if messages:
                conversations.append({
                    "id": session.id,
                    "title": f"Conversation {session.id}",
                    "created_at": session.start_time,
                    "messages": [
                        {
                            "text": msg.content,
                            "isUser": True if msg.response is None else False,
                            "audioUrl": msg.audio_url
                        }
                        for msg in messages
                    ]
                })

        return conversations
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not get conversations"
        )

@router.post("/chat/sessions")
async def create_chat_session(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new chat session"""
    try:
        # Check if there's an active session
        query = (
            select(ChatSession)
            .where(
                ChatSession.user_id == current_user["id"],
                ChatSession.end_time.is_(None)
            )
        )
        result = await db.execute(query)
        active_session = result.scalar_one_or_none()

        if active_session:
            return {"session_id": active_session.id}

        # Create new session
        new_session = ChatSession(
            user_id=current_user["id"],
            start_time=datetime.utcnow()
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)

        return {"session_id": new_session.id}
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create chat session"
        )

@router.post("/chat/sessions/{session_id}/end")
async def end_chat_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """End a chat session"""
    try:
        query = (
            select(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == current_user["id"]
            )
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session already ended"
            )

        session.end_time = datetime.utcnow()
        await db.commit()
        return {"message": "Session ended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not end chat session"
        )

@router.delete("/chat/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    try:
        # First verify the conversation belongs to the user
        query = select(ChatSession).where(
            ChatSession.id == conversation_id,
            ChatSession.user_id == current_user["id"]
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Delete all messages in the conversation
        await db.execute(
            delete(ChatMessage).where(ChatMessage.chat_session_id == conversation_id)
        )

        # Delete the conversation
        await db.execute(
            delete(ChatSession).where(ChatSession.id == conversation_id)
        )

        await db.commit()
        return {"message": "Conversation deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete conversation"
        )

@router.get("/chat/sessions/active")
async def get_active_session(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the active chat session for the user"""
    try:
        query = (
            select(ChatSession)
            .where(
                ChatSession.user_id == current_user["id"],
                ChatSession.end_time.is_(None)
            )
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            return {"session_id": None}

        return {"session_id": session.id}
    except Exception as e:
        logger.error(f"Error getting active session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not get active session"
        )
