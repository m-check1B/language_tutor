from fastapi import WebSocket, Depends
from sqlalchemy.orm import Session
from typing import Dict

from app.models import get_db, User, Conversation, Message
from app.auth import get_current_user
from app.ai_helper import generate_ai_response

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    user = await get_current_user(token, db)
    if not user:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            conversation_id, message_content = data.split(':', 1)
            conversation_id = int(conversation_id)

            # Save user message
            user_message = Message(conversation_id=conversation_id, content=message_content, is_user=True)
            db.add(user_message)
            db.commit()
            db.refresh(user_message)

            # Generate AI response
            conversation_history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
            ai_response = generate_ai_response(message_content, conversation_history)

            # Save AI message
            ai_message = Message(conversation_id=conversation_id, content=ai_response, is_user=False)
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)

            # Send both messages back to the client
            await manager.send_personal_message(f"{user_message.id}:{user_message.content}:{user_message.is_user}", user.id)
            await manager.send_personal_message(f"{ai_message.id}:{ai_message.content}:{ai_message.is_user}", user.id)

    except WebSocketDisconnect:
        manager.disconnect(user.id)
