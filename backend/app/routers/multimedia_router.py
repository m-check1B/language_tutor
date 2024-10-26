import logging
import base64
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form, Depends, Cookie, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import aiohttp
import openai
from ..config import SECRET_KEY, ALGORITHM, DEEPGRAM_API_KEY
from ..database import get_db, create_chat_session, end_chat_session, update_and_get_history
from ..auth import verify_auth_session
from ..ws import manager

router = APIRouter()
logger = logging.getLogger(__name__)

class TextRequest(BaseModel):
    prompt_text: str
    agent_name: str

@router.post("/api/multimedia/text/")
async def text_endpoint(request: Request, text_data: TextRequest, include_response: bool = False):
    logger.info("Received text message for processing.")
    
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        logger.warning("Missing authentication token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")
    
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        logger.warning("Missing auth session ID")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            logger.warning("Invalid token: user_id not found")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        logger.info(f"Token decoded successfully. User ID: {user_id}")
        
        async with get_db() as db:
            logger.info(f"Verifying auth session: {auth_session_id}")
            if not await verify_auth_session(db, auth_session_id):
                logger.warning(f"Invalid auth session: {auth_session_id}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth session")
            
            logger.info("Auth session verified successfully")
            
            agent_name = text_data.agent_name
            content = text_data.prompt_text
            logger.info(f"Processing message for user {user_id}, agent: {agent_name}")

            try:
                async with db.execute("SELECT id FROM chat_sessions WHERE user_id = ? AND end_time IS NULL", (user_id,)) as cursor:
                    result = await cursor.fetchone()
                    chat_session_id = result[0] if result else None

                if not chat_session_id:
                    chat_session_id = await create_chat_session(db, user_id)

                if chat_session_id:
                    # TODO: Implement LLM client integration
                    response_text = "This is a placeholder response. LLM integration pending."

                    if response_text:
                        logger.info(f"Generated response: {response_text}")

                        updated_history = await update_and_get_history(db, user_id, content, response_text, chat_session_id)

                        # Broadcast the entire updated history
                        history_message = {
                            "type": "history_update",
                            "chat_session_id": chat_session_id,
                            "history": [
                                {"text": h[2], "isUser": True} if idx % 2 == 0 else {"text": f"{agent_name}: {h[3]}", "isUser": False}
                                for idx, h in enumerate(updated_history)
                            ]
                        }
                        await manager.broadcast(history_message, user_id)

                        if include_response:
                            return JSONResponse(status_code=status.HTTP_200_OK, content={"response_text": response_text})
                    else:
                        logger.error(f"Failed to generate response for user {user_id}")
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate response")

                else:
                    logger.error(f"Failed to create chat session for user {user_id}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create chat session")

            except Exception as e:
                logger.error(f"Error in processing text request: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error processing text request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Request received and queued for processing"})

@router.post("/api/multimedia/deepgram_transcribe/")
async def deepgram_transcribe(
    request: Request,
    audio: UploadFile = File(...),
    agent_name: str = Form(...),
    db = Depends(get_db)
):
    try:
        token = request.headers.get("Authorization").split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        auth_session_id = request.cookies.get("auth_session_id")
        if not auth_session_id or not await verify_auth_session(db, auth_session_id):
            raise HTTPException(status_code=403, detail="Invalid auth session")

        audio_data = await audio.read()
        logger.info(f"Received audio file of size: {len(audio_data)} bytes")

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/webm"
        }
        params = {
            "model": "general",
            "tier": "enhanced",
            "diarize": "false",
            "punctuate": "true",
            "utterances": "false",
            "detect_language": "false",
            "language": "en"
        }
        logger.info(f"Sending request to Deepgram with params: {params}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepgram.com/v1/listen",
                headers=headers,
                params=params,
                data=audio_data
            ) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    logger.error(f"Deepgram API error: {error_detail}")
                    raise HTTPException(status_code=500, detail=f"Error communicating with Deepgram API: {error_detail}")

                transcription_result = await response.json()
                logger.info("Received response from Deepgram")
                transcription = transcription_result['results']['channels'][0]['alternatives'][0]['transcript']
                detected_language = transcription_result['results']['channels'][0].get('detected_language', 'unknown')
                logger.info(f"Detected language: {detected_language}")

                async with db.execute("SELECT id FROM chat_sessions WHERE user_id = ? AND end_time IS NULL", (user_id,)) as cursor:
                    chat_session = await cursor.fetchone()
                
                if not chat_session:
                    chat_session_id = await create_chat_session(db, user_id)
                else:
                    chat_session_id = chat_session[0]

                return {"transcription": transcription, "detected_language": detected_language}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

@router.get("/api/tts/config/")
async def get_tts_configuration():
    return {"voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]}

class SpeechRequest(BaseModel):
    text: str
    voice: str
    speed: float = 1.0

@router.post("/api/tts/synthesize/")
async def generate_speech(speech_request: SpeechRequest):
    try:
        if speech_request.voice not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
            raise HTTPException(status_code=400, detail="Invalid voice specified")
        if not 0.25 <= speech_request.speed <= 4.0:
            raise HTTPException(status_code=400, detail="Invalid speed specified")
        
        speech_file_path = Path("/tmp") / f"speech_{datetime.now().timestamp()}.wav"
        
        response = await openai.audio.speech.create(
            model="tts-1",
            voice=speech_request.voice,
            input=speech_request.text
        )
        
        with open(speech_file_path, "wb") as f:
            f.write(response.content)
        
        with open(speech_file_path, "rb") as audio_file:
            audio_content = audio_file.read()
        
        return {"audio_content": base64.b64encode(audio_content).decode('utf-8')}
    except Exception as e:
        logger.error(f"Error in generate_speech: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech")

@router.post("/api/reset-chat-session/")
async def reset_chat_session(request: Request, db = Depends(get_db)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        async with db.execute("SELECT id FROM chat_sessions WHERE user_id = ? AND end_time IS NULL", (user_id,)) as cursor:
            current_session = await cursor.fetchone()
        if current_session:
            await end_chat_session(db, current_session[0])

        new_chat_session_id = await create_chat_session(db, user_id)

        if not new_chat_session_id:
            raise HTTPException(status_code=500, detail="Failed to create new chat session")

        await db.execute("DELETE FROM history WHERE user_id = ? AND chat_session_id = ?", (user_id, new_chat_session_id))
        await db.commit()

        return {"message": "Chat session reset successfully", "new_chat_session_id": new_chat_session_id}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error resetting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset chat session")
