import logging
import json
from typing import List, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"Session {session_id} connected. Total connections: {len(self.active_connections[session_id])}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        self.active_connections[session_id].remove(websocket)
        if not self.active_connections[session_id]:
            del self.active_connections[session_id]
        logger.info(f"Session {session_id} disconnected. Total connections: {len(self.active_connections.get(session_id, []))}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message_to_session(self, session_id: str, message: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_text(message)
        else:
            logger.error(f"No active WebSocket connection found for session {session_id}")

    async def broadcast(self, message: str, session_id: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_text(message)
        else:
            logger.error(f"No active WebSocket connection found for session {session_id}")

manager = ConnectionManager()

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connection attempt with session ID: {session_id}")
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received data: {data} from session ID: {session_id}")
            # Handle received data here
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"WebSocket connection closed for session ID: {session_id}")

async def broadcast_chat_history(chat_session_id: str, chat_history: List[Dict]):
    message = json.dumps({
        "type": "history_update",
        "chat_session_id": chat_session_id,
        "history": chat_history
    })
    await manager.broadcast(message, chat_session_id)

async def send_ws_message(session_id: str, content: str):
    if not content:
        logger.error(f"Attempted to send an empty or undefined message to session {session_id}")
        return

    message = json.dumps({
        "type": "agent_response",
        "content": content
    })
    await manager.send_message_to_session(session_id, message)
