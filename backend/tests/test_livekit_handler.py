import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.livekit_handler import get_livekit_agent, websocket_endpoint, start_conversation, end_conversation
from app.models import User

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return User(id=1, username="testuser", email="test@example.com")

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.process_text.return_value = Mock(content="Mocked response", type="text")
    agent.process_audio.return_value = Mock(content="Mocked audio response", type="audio")
    agent.create_conversation.return_value = Mock(id="mocked_conversation_id")
    return agent

@pytest.mark.asyncio
async def test_get_livekit_agent(mock_user, mock_db):
    with patch('app.livekit_handler.MultimodalAgent') as MockAgent:
        MockAgent.return_value = Mock()
        agent = await get_livekit_agent(mock_user, mock_db)
        assert agent is not None
        MockAgent.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_endpoint(mock_user, mock_db, mock_agent):
    with patch('app.livekit_handler.WebSocket') as MockWebSocket:
        mock_websocket = MockWebSocket()
        mock_websocket.receive_json.side_effect = [
            {"type": "text", "content": "Hello"},
            {"type": "audio", "content": "base64_audio_data"},
            Exception("WebSocket disconnected")
        ]

        await websocket_endpoint(mock_websocket, "test_conversation_id", mock_user, mock_db, mock_agent)

        assert mock_websocket.accept.called
        assert mock_websocket.send_json.call_count == 2
        mock_agent.process_text.assert_called_once_with("Hello")
        mock_agent.process_audio.assert_called_once_with("base64_audio_data")

@pytest.mark.asyncio
async def test_start_conversation(mock_user, mock_db, mock_agent):
    result = await start_conversation(mock_user, mock_db, mock_agent)
    assert result == {"conversation_id": "mocked_conversation_id"}
    mock_agent.create_conversation.assert_called_once()

@pytest.mark.asyncio
async def test_end_conversation(mock_user, mock_db, mock_agent):
    result = await end_conversation("test_conversation_id", mock_user, mock_db, mock_agent)
    assert result == {"message": "Conversation ended successfully"}
    mock_agent.end_conversation.assert_called_once_with("test_conversation_id")

@pytest.mark.asyncio
async def test_websocket_endpoint_error_handling(mock_user, mock_db, mock_agent):
    with patch('app.livekit_handler.WebSocket') as MockWebSocket:
        mock_websocket = MockWebSocket()
        mock_websocket.receive_json.side_effect = [
            {"type": "invalid", "content": "Invalid message"},
            Exception("WebSocket disconnected")
        ]

        await websocket_endpoint(mock_websocket, "test_conversation_id", mock_user, mock_db, mock_agent)

        assert mock_websocket.accept.called
        mock_websocket.send_json.assert_called_once_with({"error": "Invalid input type"})

def test_start_conversation_api(test_client, mock_user, mock_agent):
    with patch('app.livekit_handler.get_current_user', return_value=mock_user), \
         patch('app.livekit_handler.get_livekit_agent', return_value=mock_agent):
        response = test_client.post("/livekit/start-conversation")
        assert response.status_code == 200
        assert response.json() == {"conversation_id": "mocked_conversation_id"}

def test_end_conversation_api(test_client, mock_user, mock_agent):
    with patch('app.livekit_handler.get_current_user', return_value=mock_user), \
         patch('app.livekit_handler.get_livekit_agent', return_value=mock_agent):
        response = test_client.post("/livekit/end-conversation/test_conversation_id")
        assert response.status_code == 200
        assert response.json() == {"message": "Conversation ended successfully"}
