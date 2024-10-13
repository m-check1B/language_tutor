from starlette.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app import models
import json
from app.ai_helper import generate_ai_response, process_voice_message, speech_to_text
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
            language = data.get('language', 'en')

            if message_type == 'audio':
                # Decode base64 audio data
                audio_data = base64.b64decode(content)
                # Process voice message
                transcription, ai_response, ai_audio = await process_voice_message(audio_data, [], language)
                
                # Save user's message (transcription) to the database
                db_message = models.Message(content=transcription, conversation_id=conversation_id, is_user=True, message_type='text', user_id=user.id)
                db.add(db_message)
                db.commit()

                # Send transcription back to the client
                await websocket.send_json({
                    'conversation_id': conversation_id,
                    'content': transcription,
                    'is_user': True,
                    'type': 'text'
                })

                # Save AI response to the database
                db_ai_message = models.Message(content=ai_response, conversation_id=conversation_id, is_user=False, message_type='text', user_id=user.id)
                db.add(db_ai_message)
                db.commit()

                # Send AI response (text or audio) back to the client
                if is_audio_mode:
                    audio_base64 = base64.b64encode(ai_audio).decode('utf-8')
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
            else:
                # Handle text messages (unchanged)
                db_message = models.Message(content=content, conversation_id=conversation_id, is_user=True, message_type=message_type, user_id=user.id)
                db.add(db_message)
                db.commit()

                await websocket.send_json({
                    'conversation_id': conversation_id,
                    'content': content,
                    'is_user': True,
                    'type': message_type
                })

                ai_response = generate_ai_response(content, [], language)
                db_ai_message = models.Message(content=ai_response, conversation_id=conversation_id, is_user=False, message_type='text', user_id=user.id)
                db.add(db_ai_message)
                db.commit()

                if is_audio_mode:
                    audio_data = text_to_speech(ai_response, language)
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
        # Read audio file content
        audio_data = await audio_file.read()
        
        # Transcribe audio to text
        transcription = await speech_to_text(audio_data)
        
        # Save transcription to database
        db_message = models.Message(content=transcription, conversation_id=conversation_id, is_user=True, message_type='audio', user_id=user.id)
        db.add(db_message)
        db.commit()

        # Generate AI response
        ai_response = generate_ai_response(transcription, [])
        db_ai_message = models.Message(content=ai_response, conversation_id=conversation_id, is_user=False, message_type='text', user_id=user.id)
        db.add(db_ai_message)
        db.commit()

        return {
            "message": "Audio received and processed",
            "transcription": transcription,
            "ai_response": ai_response
        }
    except Exception as e:
        logger.error(f"Error in handle_audio_upload: {str(e)}")
        raise
