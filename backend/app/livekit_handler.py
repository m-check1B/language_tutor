from livekit import RoomServiceClient, AccessToken, VideoGrant
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.models import User
from app.config import settings

router = APIRouter()

# Initialize LiveKit client
livekit_client = RoomServiceClient(
    settings.LIVEKIT_API_URL,
    api_key=settings.LIVEKIT_API_KEY,
    api_secret=settings.LIVEKIT_API_SECRET
)

@router.post("/create-room")
async def create_room(room_name: str, current_user: User = Depends(get_current_user)):
    try:
        room = await livekit_client.create_room(
            name=room_name,
            empty_timeout=300,  # 5 minutes
            max_participants=2  # Tutor and student
        )
        return {"room_name": room.name, "room_id": room.sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

@router.post("/join-room")
async def join_room(room_name: str, current_user: User = Depends(get_current_user)):
    try:
        # Create an access token for the user
        grant = VideoGrant(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        )
        token = AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
            grant=grant,
            identity=str(current_user.id),
            name=current_user.username
        )
        return {"access_token": token.to_jwt()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join room: {str(e)}")
