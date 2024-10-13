from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.models import get_db, User, Conversation, Message
from app.schemas import ConversationCreate, MessageCreate, ConversationResponse, MessageResponse
from app.ai_helper import generate_ai_response, process_voice_message, get_language_code
from app.middleware import subscription_required
from app.profiler import profile

router = APIRouter()

class VoiceMessageCreate(BaseModel):
    audio_content: bytes

# ... [keep all existing routes] ...

# Add these new test routes at the end of the file

@router.post("/test/conversations", response_model=ConversationResponse)
async def test_create_conversation(db: Session = Depends(get_db)):
    new_conversation = Conversation(user_id=1)  # Use a dummy user_id
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

@router.post("/test/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def test_create_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    new_message = Message(conversation_id=conversation_id, content=message.content, is_user=True)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Get conversation history
    conversation_history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    conversation_history = [{"role": "user" if msg.is_user else "assistant", "content": msg.content} for msg in conversation_history]
    
    # Generate AI response
    ai_response = generate_ai_response(message.content, conversation_history, "en")
    ai_message = Message(conversation_id=conversation_id, content=ai_response, is_user=False)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return [new_message, ai_message]

@router.post("/test/conversations/{conversation_id}/voice_messages", response_model=List[MessageResponse])
async def test_create_voice_message(
    conversation_id: int,
    voice_message: VoiceMessageCreate,
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get conversation history
    conversation_history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    conversation_history = [{"role": "user" if msg.is_user else "assistant", "content": msg.content} for msg in conversation_history]
    
    # Process voice message
    transcription, ai_response_text, ai_response_audio = process_voice_message(voice_message.audio_content, conversation_history, "en")
    
    # Save user message
    new_message = Message(conversation_id=conversation_id, content=transcription, is_user=True)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Save AI response
    ai_message = Message(conversation_id=conversation_id, content=ai_response_text, is_user=False)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return [
        MessageResponse(
            id=new_message.id,
            content=new_message.content,
            is_user=True,
            created_at=new_message.created_at,
            audio_content=voice_message.audio_content
        ),
        MessageResponse(
            id=ai_message.id,
            content=ai_message.content,
            is_user=False,
            created_at=ai_message.created_at,
            audio_content=ai_response_audio
        )
    ]
