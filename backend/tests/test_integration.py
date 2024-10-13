import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.config import settings
from app.models import get_db

# Create a test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_register_login_create_conversation():
    # Register a new user
    register_response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    )
    assert register_response.status_code == 200
    assert "username" in register_response.json()

    # Login with the new user
    login_response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    
    access_token = login_response.json()["access_token"]

    # Create a new conversation
    conversation_response = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert conversation_response.status_code == 200
    assert "id" in conversation_response.json()

    conversation_id = conversation_response.json()["id"]

    # Send a message in the conversation
    message_response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"content": "Hello, AI!"}
    )
    assert message_response.status_code == 200
    assert len(message_response.json()) == 2  # User message and AI response

    # Get conversation history
    history_response = client.get(
        f"/api/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert history_response.status_code == 200
    assert len(history_response.json()) == 2  # User message and AI response

    # Register and login a user
    client.post(
        "/auth/register",
    )
    login_response = client.post(
        "/auth/token",
    )
    access_token = login_response.json()["access_token"]

    # Create a LiveKit room
    create_room_response = client.post(
        headers={"Authorization": f"Bearer {access_token}"},
        json={"room_name": "test_room"}
    )
    assert create_room_response.status_code == 200
    assert "room_name" in create_room_response.json()
    assert "room_id" in create_room_response.json()

    # Join the LiveKit room
    join_room_response = client.post(
        headers={"Authorization": f"Bearer {access_token}"},
        json={"room_name": "test_room"}
    )
    assert join_room_response.status_code == 200
    assert "access_token" in join_room_response.json()

# Add more integration tests as needed
