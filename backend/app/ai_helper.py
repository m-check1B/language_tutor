import openai
from deepgram import Deepgram
from app.config import settings
from typing import List

openai.api_key = settings.OPENAI_API_KEY
deepgram = Deepgram(settings.DEEPGRAM_API_KEY)

def generate_ai_response(user_message: str, conversation_history: List[dict], language: str = "en") -> str:
    try:
        system_prompt = settings.LANGUAGE_TUTOR_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": f"{system_prompt} Respond in {language}. If the user's message is not in {language}, correct their language and provide the answer in {language}."},
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        response = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=messages
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return f"I'm sorry, I couldn't generate a response at this time. (in {language})"

async def speech_to_text(audio_data: bytes, language: str = "en-US") -> str:
    try:
        source = {'buffer': audio_data, 'mimetype': 'audio/wav'}
        response = await deepgram.transcription.prerecorded(source, {'language': language})
        return response['results']['channels'][0]['alternatives'][0]['transcript']
    except Exception as e:
        print(f"Error in speech-to-text conversion: {e}")
        return ""

def text_to_speech(text: str, language: str = "en", voice: str = "alloy") -> bytes:
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return b""

async def process_voice_message(audio_data: bytes, conversation_history: List[dict], language: str = "en") -> tuple:
    # Step 1: Transcribe audio to text
    transcription = await speech_to_text(audio_data, get_language_code(language))
    
    # Step 2: Generate AI response
    ai_response_text = generate_ai_response(transcription, conversation_history, language)
    
    # Step 3: Convert AI response to speech
    ai_response_audio = text_to_speech(ai_response_text, language)
    
    return transcription, ai_response_text, ai_response_audio

# Language code mappings
LANGUAGE_CODES = {
    "en": "en-US",
    "cs": "cs-CZ",
    "es": "es-ES"
}

def get_language_code(lang: str) -> str:
    return LANGUAGE_CODES.get(lang, "en-US")
