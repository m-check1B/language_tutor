import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Conversation, Message
from app.config import settings

# Create a test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user = User(username="testuser", email="test@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_create_conversation(db):
    user = User(username="convuser", email="conv@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()

    conversation = Conversation(user_id=user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    assert conversation.id is not None
    assert conversation.user_id == user.id

def test_create_message(db):
    user = User(username="msguser", email="msg@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()

    conversation = Conversation(user_id=user.id)
    db.add(conversation)
    db.commit()

    message = Message(conversation_id=conversation.id, content="Test message", is_user=True)
    db.add(message)
    db.commit()
    db.refresh(message)
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.content == "Test message"
    assert message.is_user == True

def test_user_conversations_relationship(db):
    user = User(username="reluser", email="rel@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()

    conversation1 = Conversation(user_id=user.id)
    conversation2 = Conversation(user_id=user.id)
    db.add(conversation1)
    db.add(conversation2)
    db.commit()

    db.refresh(user)
    assert len(user.conversations) == 2
    assert user.conversations[0].user_id == user.id
    assert user.conversations[1].user_id == user.id

def test_conversation_messages_relationship(db):
    user = User(username="convmsguser", email="convmsg@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()

    conversation = Conversation(user_id=user.id)
    db.add(conversation)
    db.commit()

    message1 = Message(conversation_id=conversation.id, content="Message 1", is_user=True)
    message2 = Message(conversation_id=conversation.id, content="Message 2", is_user=False)
    db.add(message1)
    db.add(message2)
    db.commit()

    db.refresh(conversation)
    assert len(conversation.messages) == 2
    assert conversation.messages[0].content == "Message 1"
    assert conversation.messages[1].content == "Message 2"
