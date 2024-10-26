import os
import sys
import logging
import base64
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Depends, Cookie, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
import aiosqlite
import aiohttp
import openai

# Import the get_db function from the appropriate module
from database_utils import get_db, verify_auth_session, create_chat_session, end_chat_session, update_and_get_history, get_history

# Initialize the router
router = APIRouter()

# Shared components
class TextRequest(BaseModel):
    prompt_text: str
    agent_name: str

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define logger
logger = logging.getLogger("media_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@router.post("/api/multimedia/text/")
async def text_endpoint(request: Request, text_data: TextRequest, include_response: bool = False):
    logger.info("Received text message for processing.")
    
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        logger.warning("Missing authentication token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")
    
    auth_session_id = request.headers.get("X-Auth-Session-ID")
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
        
        async for db in get_db():
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
                    llm_client = await get_llm_client(db, agent_name)
                    response_text = await llm_client.generate_response([{"role": "user", "content": content}])

                    if response_text:
                        print(f"Generated response: {response_text}")  # Debugging line

                        updated_history = await update_and_get_history(db, user_id, content, response_text, chat_session_id)

                        # Broadcast the entire updated history
                        history_message = json.dumps({
                            "type": "history_update",
                            "chat_session_id": chat_session_id,
                            "history": [
                                {"text": h[2], "isUser": True} if idx % 2 == 0 else {"text": f"{agent_name}: {h[3]}", "isUser": False}
                                for idx, h in enumerate(updated_history)
                            ]
                        })
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

@router.get("/")
async def read_root():
    return {"message": "Welcome to the API"}

# Additional endpoints and their handlers...

@router.post("/api/reset-chat-session/")
async def reset_chat_session(token: str = Depends(oauth2_scheme), db: aiosqlite.Connection = Depends(get_db)):
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

@router.post("/api/multimedia/deepgram_transcribe/")
async def deepgram_transcribe(
    request: Request,
    audio: UploadFile = File(...),
    agent_name: str = Form(...),
    auth_session_id: str = Cookie(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    try:
        token = request.headers.get("Authorization").split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not await verify_auth_session(db, auth_session_id):
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

                task = {
                    "user_id": user_id,
                    "chat_session_id": chat_session_id,
                    "agent_name": agent_name,
                    "content": transcription
                }

                return {"transcription": transcription, "detected_language": detected_language, "message": "Transcription received and queued for processing"}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

@router.post("/api/multimedia/audio/")
async def process_audio(audio: UploadFile = File(...), prompt_text: str = Form(...), token: str = Depends(oauth2_scheme), db: aiosqlite.Connection = Depends(get_db), request: Request = None):
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id or not await verify_auth_session(db, auth_session_id):
        raise HTTPException(status_code=403, detail="Invalid auth session")
    try:
        prompt_text = f"User uploaded an audio file. {prompt_text}"
        audio_data = await audio.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_file = Part.from_dict({"inlineData": {"data": audio_base64, "mimeType": audio.content_type}})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        async with db.execute("""
            SELECT agents.system_prompt FROM agents
            JOIN active_agent ON agents.id = active_agent.agent_id
            WHERE active_agent.user_id = :user_id
        """, {'user_id': user_id}) as cursor:
            row = await cursor.fetchone()
        if row:
            system_prompt = row[0]
        else:
            system_prompt = SYSTEM_PROMPT
        prompt = Part.from_dict({"text": f"{system_prompt}\n{prompt_text}"})
        contents = [audio_file, prompt]
        model = GenerativeModel(model_name=MODEL_ID)
        response = model.generate_content(contents)
        response_text = response.text
        async with db.execute("SELECT id FROM chat_sessions WHERE user_id = ? AND end_time IS NULL", (user_id,)) as cursor:
            chat_session = await cursor.fetchone()
        if not chat_session:
            chat_session_id = await create_chat_session(db, user_id)
        else:
            chat_session_id = chat_session[0]
        updated_history = await update_and_get_history(db, user_id, prompt_text, response_text, chat_session_id)
        return {"response_text": response_text, "chat_session_id": chat_session_id, "chat_history": updated_history}
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to process audio")

@router.post("/api/multimedia/video/")
async def process_video(video: UploadFile = File(...), prompt_text: str = Form(...), token: str = Depends(oauth2_scheme), db: aiosqlite.Connection = Depends(get_db), request: Request = None):
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id or not await verify_auth_session(db, auth_session_id):
        raise HTTPException(status_code=403, detail="Invalid auth session")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        prompt_text = f"User uploaded a video file. {prompt_text}"
        video_data = await video.read()
        video_base64 = base64.b64encode(video_data).decode('utf-8')
        video_file = Part.from_dict({"inlineData": {"data": video_base64, "mimeType": video.content_type}})

        async with db.execute("""
            SELECT agents.system_prompt FROM agents
            JOIN active_agent ON agents.id = active_agent.agent_id
            WHERE active_agent.user_id = :user_id
        """, {'user_id': user_id}) as cursor:
            row = await cursor.fetchone()
        if row:
            system_prompt = row[0]
        else:
            system_prompt = SYSTEM_PROMPT

        prompt = Part.from_dict({"text": f"{system_prompt}\n{prompt_text}"})
        contents = [video_file, prompt]
        model = GenerativeModel(model_name=MODEL_ID)
        response = model.generate_content(contents)
        response_text = response.text
        async with db.execute("SELECT id FROM chat_sessions WHERE user_id = ? AND end_time IS NULL", (user_id,)) as cursor:
            chat_session = await cursor.fetchone()
        if not chat_session:
            chat_session_id = await create_chat_session(db, user_id)
        else:
            chat_session_id = chat_session[0]
        updated_history = await update_and_get_history(db, user_id, prompt_text, response_text, chat_session_id)
        return {"response_text": response.text, "chat_session_id": chat_session_id, "chat_history": updated_history}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail="Failed to process video")

@router.post("/api/multimedia/image/")
async def process_image(
    image: UploadFile = File(...),
    prompt_text: str = Form(...),
    token: str = Depends(oauth2_scheme),
    db: aiosqlite.Connection = Depends(get_db),
    request: Request = None
):
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id or not await verify_auth_session(db, auth_session_id):
        raise HTTPException(status_code=403, detail="Invalid auth session")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        prompt_text = f"User uploaded an image file. {prompt_text}"
        image_data = await image.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        image_file = Part.from_dict({"inlineData": {"data": image_base64, "mimeType": image.content_type}})

        async with db.execute("""
            SELECT agents.system_prompt FROM agents
            JOIN active_agent ON agents.id = active_agent.agent_id
            WHERE active_agent.user_id = :user_id
        """, {'user_id': user_id}) as cursor:
            row = await cursor.fetchone()
        if row:
            system_prompt = row[0]
        else:
            system_prompt = SYSTEM_PROMPT

        prompt = Part.from_dict({"text": f"{system_prompt}\n{prompt_text}"})
        contents = [image_file, prompt]
        model = GenerativeModel(model_name=MODEL_ID)
        response = model.generate_content(contents)
        response_text = response.text
        updated_history = await update_and_get_history(db, user_id, prompt_text, response_text, auth_session_id)
        return {"response_text": response.text, "auth_session_id": auth_session_id, "chat_history": updated_history}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")

@router.post("/api/multimedia/pdf/")
async def process_pdf(pdf: UploadFile = File(...), prompt_text: str = Form(...), token: str = Depends(oauth2_scheme), db: aiosqlite.Connection = Depends(get_db), request: Request = None):
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id or not await verify_auth_session(db, auth_session_id):
        raise HTTPException(status_code=403, detail="Invalid auth session")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        prompt_text = f"User uploaded a PDF file. {prompt_text}"
        pdf_data = await pdf.read()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        pdf_file = Part.from_dict({"inlineData": {"data": pdf_base64, "mimeType": pdf.content_type}})

        async with db.execute("""
            SELECT agents.system_prompt FROM agents
            JOIN active_agent ON agents.id = active_agent.agent_id
            WHERE active_agent.user_id = :user_id
        """, {'user_id': user_id}) as cursor:
            row = await cursor.fetchone()
        if row:
            system_prompt = row[0]
        else:
            system_prompt = SYSTEM_PROMPT

        prompt = Part.from_dict({"text": f"{system_prompt}\n{prompt_text}"})
        contents = [pdf_file, prompt]
        model = GenerativeModel(model_name=MODEL_ID)
        response = model.generate_content(contents)
        response_text = response.text
        updated_history = await update_and_get_history(db, user_id, prompt_text, response_text, auth_session_id)
        return {"response_text": response.text, "auth_session_id": auth_session_id, "chat_history": updated_history}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error processing pdf: {e}")
        raise HTTPException(status_code=500, detail="Failed to process pdf")

@router.get("/api/multimedia/history/")
async def get_chat_history(token: str = Depends(oauth2_scheme), db: aiosqlite.Connection = Depends(get_db), request: Request = None):
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id or not await verify_auth_session(db, auth_session_id):
        raise HTTPException(status_code=403, detail="Invalid auth session")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        history = await get_history(db, user_id, auth_session_id)
        return {"history": history}
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.get("/ttsconfig/")
async def get_tts_configuration():
    return {"voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]}

class SpeechRequest(BaseModel):
    model: str
    input: str
    voice: str
    response_format: str = "wav"
    speed: float = 1.0

@router.post("/tts/")
async def generate_speech(speech_request: SpeechRequest):
    try:
        if speech_request.model not in ["tts-1", "tts-1-hd"]:
            raise HTTPException(status_code=400, detail="Invalid model specified")
        if speech_request.voice not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
            raise HTTPException(status_code=400, detail="Invalid voice specified")
        if not 0.25 <= speech_request.speed <= 4.0:
            raise HTTPException(status_code=400, detail="Invalid speed specified")
        
        speech_file_path = Path("/tmp") / f"speech_{datetime.now().timestamp()}.wav"
        
        with openai.audio.speech.with_streaming_response.create(
            model=speech_request.model,
            voice=speech_request.voice,
            input=speech_request.input,
        ) as response:
            response.stream_to_file(speech_file_path)
        
        with open(speech_file_path, "rb") as audio_file:
            audio_content = audio_file.read()
        
        return {"audio_content": base64.b64encode(audio_content).decode('utf-8')}
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech")
    except Exception as e:
        logger.error(f"Unexpected error in generate_speech: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
