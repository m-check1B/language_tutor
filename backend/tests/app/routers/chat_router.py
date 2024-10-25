from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from .. import schemas, models, database, auth
from ..dependencies import get_db, get_current_user
from ..websocket_handler import WebSocketManager

router = APIRouter()
ws_manager = WebSocketManager()

@router.post("/conversations", response_model=schemas.Conversation)
async def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new conversation"""
    db_conversation = models.Conversation(
        title=conversation.title,
        user_id=current_user.id,
        is_active=True
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.get("/conversations", response_model=List[schemas.Conversation])
async def get_conversations(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's conversations"""
    conversations = db.query(models.Conversation)\
        .filter(models.Conversation.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return conversations

@router.post("/chat/text", response_model=schemas.ChatResponse)
async def send_text_message(
    message: schemas.ChatMessage,
    conversation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Handle text message"""
    if not message.message:
        raise HTTPException(status_code=400, detail="Message content is required")

    # Create conversation if not exists
    if not conversation_id:
        db_conversation = models.Conversation(
            title=message.message[:50] + "...",
            user_id=current_user.id
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        conversation_id = db_conversation.id

    # Save user message
    db_message = models.Message(
        content=message.message,
        conversation_id=conversation_id,
        user_id=current_user.id,
        is_user_message=True
    )
    db.add(db_message)
    db.commit()

    # Generate AI response
    # TODO: Implement AI response generation
    ai_response = "This is a placeholder AI response."

    # Save AI response
    db_ai_message = models.Message(
        content=ai_response,
        conversation_id=conversation_id,
        user_id=current_user.id,
        is_user_message=False
    )
    db.add(db_ai_message)
    db.commit()

    return schemas.ChatResponse(response=ai_response)

@router.post("/chat/audio", response_model=schemas.ChatResponse)
async def send_audio_message(
    audio: UploadFile = File(...),
    conversation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Handle audio message"""
    if not audio.filename.endswith(('.wav', '.mp3', '.ogg')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # TODO: Implement audio file storage
    audio_url = f"/audio/{audio.filename}"  # Placeholder URL

    # Create conversation if not exists
    if not conversation_id:
        db_conversation = models.Conversation(
            title=f"Voice conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            user_id=current_user.id
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        conversation_id = db_conversation.id

    # Save user message
    db_message = models.Message(
        audio_url=audio_url,
        conversation_id=conversation_id,
        user_id=current_user.id,
        is_user_message=True
    )
    db.add(db_message)
    db.commit()

    # TODO: Implement speech-to-text and AI response generation
    ai_response = "This is a placeholder AI response to audio message."

    # Save AI response
    db_ai_message = models.Message(
        content=ai_response,
        conversation_id=conversation_id,
        user_id=current_user.id,
        is_user_message=False
    )
    db.add(db_ai_message)
    db.commit()

    return schemas.ChatResponse(response=ai_response)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Validate message
            ws_message = schemas.WSMessage(**message_data)
            
            # TODO: Process message based on type (text/audio)
            # For now, just echo back
            response = schemas.WSResponse(
                type=ws_message.type,
                content=f"Echo: {ws_message.content}",
                conversation_id=ws_message.conversation_id
            )
            
            await websocket.send_text(response.json())
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        ws_manager.disconnect(client_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a conversation"""
    conversation = db.query(models.Conversation)\
        .filter(models.Conversation.id == conversation_id)\
        .filter(models.Conversation.user_id == current_user.id)\
        .first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted"}
