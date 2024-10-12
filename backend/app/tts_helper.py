import requests
from app.config import settings

def text_to_speech(text: str) -> bytes:
    try:
        url = "https://api.groq.com/v1/text-to-speech"  # Placeholder URL for Groq API
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.GROQ_API_KEY}"  # Assuming an API key is needed
        }
        data = {
            "text": text,
            "voice": "default",  # Adjust based on Groq's API requirements
            "options": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return b""
