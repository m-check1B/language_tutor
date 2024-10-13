import openai
import requests
from google.cloud import texttospeech
from app.config import settings
from typing import List

openai.api_key = settings.OPENAI_API_KEY

def generate_ai_response(user_message: str, conversation_history: List[dict]) -> str:
    try:
        messages = [
            {"role": "system", "content": "You are a helpful language tutor."},
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm sorry, I couldn't generate a response at this time."

def speech_to_text(audio_data: bytes) -> str:
    try:
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"  # Adjust based on the audio format
        }
        response = requests.post(url, headers=headers, data=audio_data)
        response.raise_for_status()
        return response.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
    except Exception as e:
        print(f"Error in speech-to-text conversion: {e}")
        return ""

def text_to_speech(text: str, language_code: str = "en-US") -> bytes:
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        return response.audio_content
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return b""
