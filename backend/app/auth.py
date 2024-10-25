from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import requests
from app.models import User
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL

TEST_TOKEN = "test_token_for_language_tutor"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/auth", json={"email": email, "password": password})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error authenticating user: {e}")
        return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user(db: Session, username: str, email: str, password: str):
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json={"username": username, "email": email, "password": password})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating user: {e}")
        return None
