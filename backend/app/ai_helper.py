import openai
import requests
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_ai_response(user_message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful language tutor."},
                {"role": "user", "content": user_message}
            ]
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
        return response.json().get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
    except Exception as e:
        print(f"Error in speech-to-text conversion: {e}")
        return ""
