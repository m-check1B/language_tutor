import pytest
from unittest.mock import patch, MagicMock
from app.ai_helper import speech_to_text, generate_ai_response, process_voice_message

@pytest.mark.asyncio
async def test_speech_to_text():
    mock_audio_data = b'fake_audio_data'
    mock_transcription = "This is a test transcription."

    with patch('app.ai_helper.deepgram') as mock_deepgram:
        mock_deepgram.transcription.prerecorded.return_value = {
            'results': {
                'channels': [{'alternatives': [{'transcript': mock_transcription}]}]
            }
        }

        result = await speech_to_text(mock_audio_data, 'en-US')
        assert result == mock_transcription
        mock_deepgram.transcription.prerecorded.assert_called_once_with(
            {'buffer': mock_audio_data, 'mimetype': 'audio/wav'},
            {'language': 'en-US'}
        )

def test_generate_ai_response():
    mock_user_message = "Hello, AI!"
    mock_conversation_history = []
    mock_language = "en"
    mock_ai_response = "Hello! How can I assist you today?"

    with patch('app.ai_helper.openai.ChatCompletion.create') as mock_create:
        mock_create.return_value.choices[0].message = {'content': mock_ai_response}

        result = generate_ai_response(mock_user_message, mock_conversation_history, mock_language)
        assert result == mock_ai_response
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_process_voice_message():
    mock_audio_data = b'fake_audio_data'
    mock_conversation_history = []
    mock_language = "en"
    mock_transcription = "This is a test transcription."
    mock_ai_response = "This is a test AI response."
    mock_audio_response = b'fake_audio_response'

    with patch('app.ai_helper.speech_to_text', return_value=mock_transcription), \
         patch('app.ai_helper.generate_ai_response', return_value=mock_ai_response), \
         patch('app.ai_helper.text_to_speech', return_value=mock_audio_response):

        transcription, ai_response_text, ai_response_audio = await process_voice_message(
            mock_audio_data, mock_conversation_history, mock_language
        )

        assert transcription == mock_transcription
        assert ai_response_text == mock_ai_response
        assert ai_response_audio == mock_audio_response

if __name__ == "__main__":
    pytest.main()
