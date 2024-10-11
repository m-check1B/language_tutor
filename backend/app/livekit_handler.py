from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.models import User
from app.config import settings
import jwt
import time

router = APIRouter()

def create_token(room_name: str, user_id: str):
    now = int(time.time())
    exp = now + 3600  # Token expires in 1 hour

    claim = {
        "iss": settings.LIVEKIT_API_KEY,
        "nbf": now,
        "exp": exp,
        "sub": user_id,
        "room": room_name,
        "video": {
            "room_join": True,
            "room": room_name,
            "can_publish": True,
            "can_subscribe": True
        }
    }

    token = jwt.encode(claim, settings.LIVEKIT_API_SECRET, algorithm='HS256')
    return token

@router.post("/create-room")
async def create_room(room_name: str, current_user: User = Depends(get_current_user)):
    try:
        token = create_token(room_name, str(current_user.id))
        return {"room_name": room_name, "access_token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

@router.post("/join-room")
async def join_room(room_name: str, current_user: User = Depends(get_current_user)):
    try:
        token = create_token(room_name, str(current_user.id))
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join room: {str(e)}")
