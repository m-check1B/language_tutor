import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.config import settings
from app.models import get_db

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

def test_register():
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "username" in response.json()
    assert "email" in response.json()

def test_login():
    # First, register a user
    client.post(
        "/auth/register",
        json={"username": "loginuser", "email": "login@example.com", "password": "loginpassword"}
    )
    
    # Now, try to login
    response = client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "loginpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_login_invalid_credentials():
    response = client.post(
        "/auth/token",
        data={"username": "invaliduser", "password": "invalidpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

# Add more tests as needed
