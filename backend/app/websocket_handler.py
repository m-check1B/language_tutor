from starlette.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app import models
import json
from app.ai_helper import generate_ai_response
from app.tts_helper import text_to_speech
import base64
from app.auth import get_current_user_from_token
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def websocket_endpoint(websocket: WebSocket, token: str, db: Session):
    try:
        # Authenticate the user
        user = await get_current_user_from_token(token, db)
        if not user:
            await websocket.close(code=4001)
            return
    except HTTPException:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            conversation_id = data['conversation_id']
            message_type = data['type']
            content = data['content']
            is_audio_mode = data['is_audio_mode']

            # Save the message to the database
            db_message = models.Message(content=content, conversation_id=conversation_id, is_user=True, message_type=message_type, user_id=user.id)
            db.add(db_message)
            db.commit()

            # Send the message back to the client
            await websocket.send_json({
                'conversation_id': conversation_id,
                'content': content,
                'is_user': True,
                'type': message_type
            })

            # Generate AI response
            ai_response = generate_ai_response(content)
            db_ai_message = models.Message(content=ai_response, conversation_id=conversation_id, is_user=False, message_type='text', user_id=user.id)
            db.add(db_ai_message)
            db.commit()

            if is_audio_mode:
                # Convert AI response to speech
                audio_data = text_to_speech(ai_response)
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                await websocket.send_json({
                    'conversation_id': conversation_id,
                    'content': audio_base64,
                    'is_user': False,
                    'type': 'audio'
                })
            else:
                await websocket.send_json({
                    'conversation_id': conversation_id,
                    'content': ai_response,
                    'is_user': False,
                    'type': 'text'
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user.id}")
    except Exception as e:
        logger.error(f"Error in websocket_endpoint: {str(e)}")
    finally:
        # Clean up any resources if needed
        pass

async def handle_audio_upload(audio_file, conversation_id: int, user: models.User, db: Session):
    try:
        # Process the audio file (e.g., save it, transcribe it)
        # For now, we'll just save a placeholder message
        content = "Audio message received"
        db_message = models.Message(content=content, conversation_id=conversation_id, is_user=True, message_type='audio', user_id=user.id)
        db.add(db_message)
        db.commit()

        # Generate AI response
        ai_response = generate_ai_response(content)
        db_ai_message = models.Message(content=ai_response, conversation_id=conversation_id, is_user=False, message_type='text', user_id=user.id)
        db.add(db_ai_message)
        db.commit()

        return {"message": "Audio received and processed"}
    except Exception as e:
        logger.error(f"Error in handle_audio_upload: {str(e)}")
        raise
