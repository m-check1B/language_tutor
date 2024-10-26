from fastapi import WebSocket
from typing import Dict, Set, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Regular user connections: user_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Admin connections: user_id -> Set[WebSocket]
        self.admin_connections: Dict[int, Set[WebSocket]] = {}
        # Last activity timestamp for each connection
        self.last_activity: Dict[WebSocket, datetime] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a regular user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        self.last_activity[websocket] = datetime.utcnow()
        logger.info(f"User {user_id} connected. Active connections: {len(self.active_connections)}")

    async def connect_admin(self, websocket: WebSocket, user_id: int):
        """Connect an admin user"""
        await websocket.accept()
        if user_id not in self.admin_connections:
            self.admin_connections[user_id] = set()
        self.admin_connections[user_id].add(websocket)
        self.last_activity[websocket] = datetime.utcnow()
        logger.info(f"Admin {user_id} connected. Active admin connections: {len(self.admin_connections)}")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a regular user"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        if websocket in self.last_activity:
            del self.last_activity[websocket]
        logger.info(f"User {user_id} disconnected. Active connections: {len(self.active_connections)}")

    async def disconnect_admin(self, websocket: WebSocket, user_id: int):
        """Disconnect an admin user"""
        if user_id in self.admin_connections:
            self.admin_connections[user_id].discard(websocket)
            if not self.admin_connections[user_id]:
                del self.admin_connections[user_id]
        if websocket in self.last_activity:
            del self.last_activity[websocket]
        logger.info(f"Admin {user_id} disconnected. Active admin connections: {len(self.admin_connections)}")

    async def broadcast_message(self, user_id: int, message: str, session_id: Optional[str] = None):
        """Broadcast a message to all connected users in the same session"""
        try:
            data = {
                "type": "message",
                "user_id": user_id,
                "content": message,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to all users in the session
            for uid, connections in self.active_connections.items():
                for connection in connections:
                    try:
                        await connection.send_json(data)
                        self.last_activity[connection] = datetime.utcnow()
                    except Exception as e:
                        logger.error(f"Error sending message to user {uid}: {e}")
                        await self.disconnect(connection, uid)

            # Send to all admin connections
            for uid, connections in self.admin_connections.items():
                for connection in connections:
                    try:
                        await connection.send_json(data)
                        self.last_activity[connection] = datetime.utcnow()
                    except Exception as e:
                        logger.error(f"Error sending message to admin {uid}: {e}")
                        await self.disconnect_admin(connection, uid)

        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    async def broadcast_system_message(self, message: str):
        """Broadcast a system message to all connected users"""
        data = {
            "type": "system",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all regular users
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(data)
                    self.last_activity[connection] = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error sending system message to user {user_id}: {e}")
                    await self.disconnect(connection, user_id)

        # Send to all admins
        for user_id, connections in self.admin_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(data)
                    self.last_activity[connection] = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error sending system message to admin {user_id}: {e}")
                    await self.disconnect_admin(connection, user_id)

    async def broadcast_user_disconnect(self, user_id: int):
        """Broadcast user disconnect event to admins"""
        data = {
            "type": "user_disconnect",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for admin_id, connections in self.admin_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(data)
                    self.last_activity[connection] = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error sending disconnect event to admin {admin_id}: {e}")
                    await self.disconnect_admin(connection, admin_id)

    def get_connection_stats(self):
        """Get statistics about current connections"""
        return {
            "users": {
                "total": len(self.active_connections),
                "connections": {
                    user_id: len(connections) 
                    for user_id, connections in self.active_connections.items()
                }
            },
            "admins": {
                "total": len(self.admin_connections),
                "connections": {
                    user_id: len(connections)
                    for user_id, connections in self.admin_connections.items()
                }
            }
        }

# Create a global instance of the connection manager
manager = ConnectionManager()
