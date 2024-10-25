from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        """Connect a new client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: int):
        """Disconnect a client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: int):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str, exclude: int = None):
        """Broadcast a message to all connected clients except the excluded one"""
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_text(message)

    async def send_to_room(self, message: str, room_id: int, exclude: int = None):
        """Send a message to all clients in a specific room"""
        # TODO: Implement room-based message routing
        # This would require maintaining a mapping of room_id to client_ids
        pass

    def get_connection(self, client_id: int) -> WebSocket:
        """Get the WebSocket connection for a specific client"""
        return self.active_connections.get(client_id)

    def is_connected(self, client_id: int) -> bool:
        """Check if a client is connected"""
        return client_id in self.active_connections

    async def close_connection(self, client_id: int):
        """Close a specific client connection"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].close()
            self.disconnect(client_id)

    async def close_all_connections(self):
        """Close all active connections"""
        for client_id in list(self.active_connections.keys()):
            await self.close_connection(client_id)
