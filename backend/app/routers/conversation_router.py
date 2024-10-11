from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import get_db, User, Conversation, Message
from app.auth import get_current_user
from app.schemas import ConversationCreate, MessageCreate, ConversationResponse, MessageResponse
from app.ai_helper import generate_ai_response

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_conversation = Conversation(user_id=current_user.id)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

@router.get("/conversations", response_model=List[ConversationResponse])
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    return conversations

@router.post("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def create_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
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

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    return messages
