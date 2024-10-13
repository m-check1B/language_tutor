from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import requests
from app.models import User, get_db
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL  # URL for the auth_and_paywall service

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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        user_data = response.json()
        return user_data
    except requests.RequestException:
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_subscription_status(current_user: dict = Depends(get_current_user)):
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/subscription", headers={"Authorization": f"Bearer {current_user['token']}"})
        response.raise_for_status()
        subscription_data = response.json()
        if not subscription_data.get("is_subscribed"):
            raise HTTPException(status_code=403, detail="Active subscription required")
        return subscription_data
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error checking subscription status: {str(e)}")

def create_user(db: Session, username: str, email: str, password: str):
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json={"username": username, "email": email, "password": password})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating user: {e}")
        return None
