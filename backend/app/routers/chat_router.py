import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..auth import get_current_user
from ..models import ChatSession, ChatMessage
from sqlalchemy import select, delete

router = APIRouter(prefix="/api")  # Add prefix here
logger = logging.getLogger(__name__)

@router.get("/chat/conversations")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    try:
        query = select(ChatSession).where(ChatSession.user_id == current_user["id"])
        result = await db.execute(query)
        sessions = result.scalars().all()

        conversations = []
        for session in sessions:
            messages_query = select(ChatMessage).where(ChatMessage.session_id == session.id)
            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()
            
            conversations.append({
                "id": session.id,
                "title": f"Conversation {session.id}",
                "created_at": session.created_at,
                "messages": [
                    {
                        "text": msg.content,
                        "isUser": msg.is_user,
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
            delete(ChatMessage).where(ChatMessage.session_id == conversation_id)
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
