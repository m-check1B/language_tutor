import logging
import json
from typing import List, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
import jwt
from ..config import SECRET_KEY, ALGORITHM
from ..database import get_db
from ..auth import verify_auth_session

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections.get(user_id, []))}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.active_connections[user_id].remove(connection)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        else:
            logger.error(f"No active WebSocket connection found for user {user_id}")

manager = ConnectionManager()
router = APIRouter()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db = Depends(get_db)):
    try:
        # Verify token and get user_id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connect and handle messages
        await manager.connect(websocket, user_id)
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                    message_type = message_data.get("type")
                    content = message_data.get("content")

                    if message_type == "ping":
                        await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                    else:
                        # Handle other message types as needed
                        await manager.broadcast(
                            {
                                "type": "message",
                                "content": content,
                                "user_id": user_id
                            },
                            user_id
                        )
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received from user {user_id}")
                    continue

        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            await manager.broadcast(
                {
                    "type": "system",
                    "content": "Client disconnected",
                    "user_id": user_id
                },
                user_id
            )
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

async def broadcast_chat_history(user_id: str, chat_history: List[Dict]):
    """
    Broadcast chat history to all connections for a user
    """
    message = {
        "type": "history_update",
        "history": chat_history
    }
    await manager.broadcast(message, user_id)

async def send_message(user_id: str, content: str, is_error: bool = False):
    """
    Send a message to all connections for a user
    """
    if not content:
        logger.error(f"Attempted to send an empty message to user {user_id}")
        return

    message = {
        "type": "error" if is_error else "message",
        "content": content
    }
    await manager.broadcast(message, user_id)
