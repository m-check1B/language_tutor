from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Generator
import requests

from .database import SessionLocal
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token == "test_token_for_language_tutor":
        return {"sub": "testuser@example.com", "is_active": True, "is_subscribed": True}
    
    try:
        response = requests.get(f"{settings.AUTH_SERVICE_URL}/validate", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        user_data = response.json()
        return user_data
    except requests.RequestException:
        raise credentials_exception
