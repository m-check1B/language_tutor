import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_helper import generate_ai_response, process_voice_message
from app.config import settings

def test_text_conversations():
    languages = ["en", "cs", "es"]
    test_cases = [
        "How do I introduce myself?",
        "What's the difference between 'their', 'there', and 'they're'?",
        "Can you explain the past tense?",
        "How do I ask for directions?",
        "What are some common phrases for ordering food?"
    ]

    for lang in languages:
        print(f"\nTesting text conversations in {lang.upper()}:")
        conversation_history = []
        for case in test_cases:
            response = generate_ai_response(case, conversation_history, lang)
            print(f"Q: {case}")
            print(f"A: {response}\n")
            conversation_history.append({"role": "user", "content": case})
            conversation_history.append({"role": "assistant", "content": response})

def test_voice_conversations():
    languages = ["en-US", "cs-CZ", "es-ES"]
    test_cases = [
        b"This is a simulated voice message for testing.",
        b"Toto je simulovaná hlasová zpráva pro testování.",
        b"Este es un mensaje de voz simulado para pruebas."
    ]

    for lang, case in zip(languages, test_cases):
        print(f"\nTesting voice conversations in {lang}:")
        conversation_history = []
        transcription, ai_response_text, ai_response_audio = process_voice_message(case, conversation_history, lang)
        print(f"Transcription: {transcription}")
        print(f"AI Response: {ai_response_text}")
        print(f"Audio response length: {len(ai_response_audio)} bytes\n")

if __name__ == "__main__":
    print(f"Using system prompt: {settings.LANGUAGE_TUTOR_SYSTEM_PROMPT}\n")
    test_text_conversations()
    test_voice_conversations()
