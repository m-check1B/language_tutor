from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import aiofiles
import os
import uuid
from datetime import datetime
from openai import AsyncOpenAI
import magic
from pathlib import Path
import json
import PyPDF2
import io
import base64

from .. import schemas, models, auth
from ..database import get_db
from ..config import Settings

router = APIRouter()
settings = Settings()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Initialize Deepgram client if API key is available
deepgram = None
if settings.DEEPGRAM_API_KEY and settings.DEEPGRAM_API_KEY != "your-deepgram-api-key":
    try:
        from deepgram import Deepgram
        deepgram = Deepgram(settings.DEEPGRAM_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Deepgram: {str(e)}")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_mime_type(file_content: bytes) -> str:
    return magic.from_buffer(file_content, mime=True)

async def save_upload_file(file: UploadFile) -> str:
    content = await file.read()
    mime_type = get_mime_type(content)
    ext = mime_type.split('/')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    async with aiofiles.open(filepath, 'wb') as out_file:
        await out_file.write(content)
    
    return filepath

async def process_text_file(filepath: str) -> str:
    async with aiofiles.open(filepath, 'r', encoding='utf-8') as file:
        return await file.read()

async def process_pdf_file(filepath: str) -> str:
    text = ""
    with open(filepath, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

async def process_image_file(filepath: str) -> str:
    try:
        with open(filepath, 'rb') as image_file:
            response = await openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please describe this image in detail."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@router.post("/transcribe/", response_model=schemas.FileUploadResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not deepgram:
        raise HTTPException(status_code=503, detail="Speech recognition service is not available")

    filepath = await save_upload_file(file)
    
    try:
        with open(filepath, 'rb') as audio:
            payload = {
                "smart_format": True,
                "model": "nova-2-enterprise",
                "language": "en-US"
            }
            
            response = await deepgram.transcription.prerecorded.v('1').transcribe_file(audio, payload)
            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            
            return {
                "text": transcript,
                "media_type": "audio",
                "media_url": filepath
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@router.post("/tts/", response_model=schemas.FileUploadResponse)
async def text_to_speech(
    tts_request: schemas.TTSRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        speech_file_path = Path(UPLOAD_DIR) / f"speech_{datetime.now().timestamp()}.mp3"
        
        response = await openai_client.audio.speech.create(
            model=tts_request.model,
            voice=tts_request.voice,
            input=tts_request.text,
            speed=tts_request.speed
        )
        
        response.stream_to_file(speech_file_path)
        
        return {
            "text": tts_request.text,
            "media_type": "audio",
            "media_url": str(speech_file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-speech conversion failed: {str(e)}")

@router.post("/process-file/", response_model=schemas.FileUploadResponse)
async def process_file(
    file: UploadFile = File(...),
    text: Optional[str] = Form(None),
    tts_settings: Optional[str] = Form(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    filepath = await save_upload_file(file)
    content = await file.read()
    mime_type = get_mime_type(content)
    media_type = mime_type.split('/')[0]
    processed_text = ""

    try:
        if mime_type == 'text/plain':
            processed_text = await process_text_file(filepath)
        elif mime_type == 'application/pdf':
            processed_text = await process_pdf_file(filepath)
        elif media_type == 'image':
            processed_text = await process_image_file(filepath)
        elif media_type == 'video':
            # Extract audio from video and transcribe
            processed_text = "Video processing not implemented yet"
        elif media_type == 'audio':
            if not deepgram:
                raise HTTPException(status_code=503, detail="Speech recognition service is not available")
            # Transcribe audio
            processed_text = await transcribe_audio(file, current_user, db)

        # Generate AI response
        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful language tutor."},
                {"role": "user", "content": f"Please help me understand this content: {processed_text}"}
            ]
        )
        ai_response = response.choices[0].message.content

        # Generate speech if TTS settings provided
        audio_url = None
        if tts_settings:
            settings_dict = json.loads(tts_settings)
            if not settings_dict.get('isSilentMode', False):
                tts_response = await text_to_speech(
                    schemas.TTSRequest(
                        text=ai_response,
                        voice=settings_dict.get('voice', 'alloy'),
                        speed=float(settings_dict.get('speed', 1.0)),
                        model="tts-1-hd"
                    ),
                    current_user,
                    db
                )
                audio_url = tts_response.media_url

        return {
            "text": ai_response,
            "media_type": media_type,
            "media_url": audio_url or filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@router.get("/tts-voices/")
async def get_tts_voices(
    current_user: models.User = Depends(auth.get_current_user)
):
    return {
        "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "models": ["tts-1", "tts-1-hd"]
    }

@router.post("/tts-preference/", response_model=schemas.TTSVoicePreference)
async def set_tts_preference(
    preference: schemas.TTSVoicePreferenceCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        db_preference = await db.query(models.TTSVoicePreference).filter(
            models.TTSVoicePreference.user_id == current_user.id
        ).first()
        
        if db_preference:
            for key, value in preference.dict().items():
                setattr(db_preference, key, value)
        else:
            db_preference = models.TTSVoicePreference(
                **preference.dict(),
                user_id=current_user.id
            )
            db.add(db_preference)
        
        await db.commit()
        await db.refresh(db_preference)
        return db_preference
