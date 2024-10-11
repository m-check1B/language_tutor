import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, User
from app.config import settings
from app.models import get_db
from app.auth import create_access_token

# Create a test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
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

@pytest.fixture
def test_user(db):
    user = User(username="testuser", email="test@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def token(test_user):
    return create_access_token(data={"sub": test_user.username})

def test_create_conversation(token):
    response = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_user_conversations(token, test_user):
    # First, create a conversation
    client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now, get the user's conversations
    response = client.get(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_create_message(token, test_user):
    # First, create a conversation
    conversation_response = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    conversation_id = conversation_response.json()["id"]
    
    # Now, create a message
    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Test message"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2  # User message and AI response
    assert response.json()[0]["content"] == "Test message"

def test_get_conversation_messages(token, test_user):
    # First, create a conversation and a message
    conversation_response = client.post(
        "/api/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    conversation_id = conversation_response.json()["id"]
    client.post(
        f"/api/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Test message"}
    )
    
    # Now, get the conversation messages
    response = client.get(
        f"/api/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2  # User message and AI response

# Add more tests as needed
