from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth import authenticate_user, create_access_token, create_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.config import settings

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user: UserCreate):
    new_user = create_user(user.username, user.email, user.password)
    if not new_user:
        raise HTTPException(status_code=400, detail="Unable to register user")
    return {"username": new_user["username"], "email": new_user["email"]}

@router.post("/login")
async def login(user_data: UserLogin):
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user  # The external auth service should return the access token

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm):
    user = authenticate_user(form_data.username, form_data.password)  # OAuth2PasswordRequestForm uses 'username' field for email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user  # The external auth service should return the access token

__all__ = ["router"]
