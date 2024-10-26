import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        logger.info("WebSocket connection manager initialized")

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connection established for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"WebSocket connection closed for user {user_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                    logger.debug(f"Message sent to user {user_id}: {message}")
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    await self.handle_disconnection(connection, user_id)

    async def broadcast(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
        logger.debug(f"Broadcast message sent: {message}")

    async def handle_disconnection(self, websocket: WebSocket, user_id: int):
        try:
            await websocket.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket for user {user_id}: {e}")
        finally:
            self.disconnect(websocket, user_id)

manager = ConnectionManager()
