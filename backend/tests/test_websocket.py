import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, User, Conversation
from app.config import settings
from app.models import get_db
from app.auth import create_access_token

# Create a test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_websocket.db"
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
    user = User(username="wsuser", email="ws@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def token(test_user):
    return create_access_token(data={"sub": test_user.username})

@pytest.fixture
def conversation(db, test_user):
    conversation = Conversation(user_id=test_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def test_websocket_connection(token):
    with client.websocket_connect(f"/ws/{token}") as websocket:
        data = websocket.receive_text()
        assert data == "Connected to WebSocket"

def test_websocket_send_receive(token, conversation):
    with client.websocket_connect(f"/ws/{token}") as websocket:
        websocket.receive_text()  # Consume the connection message
        
        message = f"{conversation.id}:Hello, WebSocket!"
        websocket.send_text(message)
        
        # Receive user message
        response = websocket.receive_text()
        assert ":Hello, WebSocket!:True" in response
        
        # Receive AI response
        ai_response = websocket.receive_text()
        assert ":False" in ai_response

def test_websocket_invalid_token():
    with pytest.raises(Exception):  # The exact exception type may vary
        client.websocket_connect("/ws/invalid_token")

# Add more WebSocket tests as needed
