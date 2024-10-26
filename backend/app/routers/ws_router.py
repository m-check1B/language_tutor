from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import verify_auth_session
from ..models import User
from ..ws import ConnectionManager
from ..database import get_db
import logging
import json
import jwt
from typing import Optional
from ..config import SECRET_KEY, ALGORITHM

router = APIRouter()
manager = ConnectionManager()
logger = logging.getLogger(__name__)

async def get_user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    """Get user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
            
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except jwt.JWTError:
        return None

@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time communication"""
    try:
        # Get auth session ID from query params
        auth_session_id = websocket.query_params.get("session")
        if not auth_session_id:
            await websocket.close(code=4001, reason="Missing auth session")
            return

        # Verify auth session
        if not await verify_auth_session(db, auth_session_id):
            await websocket.close(code=4001, reason="Invalid or expired session")
            return

        # Get user from token
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return

        # Accept connection
        await manager.connect(websocket, user.id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {data}")
                    continue

                # Process message based on type
                message_type = message_data.get("type")
                if message_type == "chat":
                    # Handle chat message
                    await manager.broadcast_message(
                        user.id,
                        message_data.get("content", ""),
                        message_data.get("session_id")
                    )
                elif message_type == "heartbeat":
                    # Respond to heartbeat
                    await websocket.send_json({
                        "type": "heartbeat",
                        "status": "alive"
                    })
                else:
                    logger.warning(f"Unknown message type: {message_type}")

        except WebSocketDisconnect:
            await manager.disconnect(websocket, user.id)
            await manager.broadcast_user_disconnect(user.id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await manager.disconnect(websocket, user.id)
            await websocket.close(code=1011, reason="Internal server error")

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1011, reason="Internal server error")

@router.websocket("/ws/admin/{token}")
async def admin_websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Admin WebSocket endpoint for monitoring and management"""
    try:
        # Get auth session ID from query params
        auth_session_id = websocket.query_params.get("session")
        if not auth_session_id:
            await websocket.close(code=4001, reason="Missing auth session")
            return

        # Verify auth session
        if not await verify_auth_session(db, auth_session_id):
            await websocket.close(code=4001, reason="Invalid or expired session")
            return

        # Get user from token
        user = await get_user_from_token(token, db)
        if not user or not user.is_admin:
            await websocket.close(code=4003, reason="Admin access required")
            return

        await manager.connect_admin(websocket, user.id)
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    admin_data = json.loads(data)
                    # Process admin commands
                    command = admin_data.get("command")
                    if command == "get_stats":
                        stats = manager.get_connection_stats()
                        await websocket.send_json({
                            "type": "stats",
                            "data": stats
                        })
                    elif command == "broadcast":
                        await manager.broadcast_system_message(
                            admin_data.get("message", "")
                        )
                    else:
                        logger.warning(f"Unknown admin command: {command}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in admin message: {data}")
        except WebSocketDisconnect:
            await manager.disconnect_admin(websocket, user.id)
        except Exception as e:
            logger.error(f"Admin WebSocket error: {e}")
            await manager.disconnect_admin(websocket, user.id)
            await websocket.close(code=1011, reason="Internal server error")
    except Exception as e:
        logger.error(f"Admin WebSocket connection error: {e}")
        await websocket.close(code=1011, reason="Internal server error")

@router.get("/ws/status")
async def get_websocket_status():
    """Get current WebSocket connection status"""
    return {
        "active_connections": manager.get_connection_stats(),
        "status": "operational"
    }
