from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.models import get_db, User, Conversation, Message
from app.schemas import ConversationCreate, MessageCreate, ConversationResponse, MessageResponse
from app.ai_helper import generate_ai_response, speech_to_text, text_to_speech
from app.middleware import subscription_required

router = APIRouter()

class VoiceMessageCreate(BaseModel):
    audio_content: bytes

@router.post("/conversations", response_model=ConversationResponse)
@subscription_required
async def create_conversation(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    new_conversation = Conversation(user_id=current_user["id"])
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

@router.get("/conversations", response_model=List[ConversationResponse])
@subscription_required
async def get_user_conversations(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user["id"]).all()
    return conversations

@router.post("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
@subscription_required
async def create_message(
    conversation_id: int,
    message: MessageCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user["id"]).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    new_message = Message(conversation_id=conversation_id, content=message.content, is_user=True)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Get conversation history
    conversation_history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    
    # Generate AI response
    ai_response = generate_ai_response(message.content, conversation_history)
    ai_message = Message(conversation_id=conversation_id, content=ai_response, is_user=False)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return [new_message, ai_message]

@router.post("/conversations/{conversation_id}/voice_messages", response_model=List[MessageResponse])
@subscription_required
async def create_voice_message(
    conversation_id: int,
    voice_message: VoiceMessageCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user["id"]).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Transcribe audio to text
    transcription = speech_to_text(voice_message.audio_content)
    
    new_message = Message(conversation_id=conversation_id, content=transcription, is_user=True)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Get conversation history
    conversation_history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    
    # Generate AI response
    ai_response_text = generate_ai_response(transcription, conversation_history)
    ai_message = Message(conversation_id=conversation_id, content=ai_response_text, is_user=False)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    # Convert AI response to speech
    ai_response_audio = text_to_speech(ai_response_text)
    
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

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
@subscription_required
async def get_conversation_messages(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user["id"]).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    return messages
