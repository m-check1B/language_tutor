import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..database import get_db
from ..auth import (
    authenticate_user,
    create_access_token,
    create_auth_session,
    end_auth_session,
    register_user
)
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, SESSION_COOKIE_NAME

router = APIRouter()
logger = logging.getLogger(__name__)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class UserResponse(BaseModel):
    username: str
    email: EmailStr

@router.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db = Depends(get_db)):
    """Register a new user"""
    try:
        user = await register_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return UserResponse(username=user["username"], email=user["email"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user"
        )

@router.post("/api/auth/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    """Login user and create session"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"user_id": user["id"]},
        expires_delta=access_token_expires
    )

    # Create auth session
    session_id = await create_auth_session(db, user["id"])
    
    # Set session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"]
    }

@router.post("/api/auth/logout")
async def logout(
    response: Response,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Logout user and end session"""
    if session_id:
        await end_auth_session(db, session_id)
    
    # Clear session cookie
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return {"message": "Successfully logged out"}

@router.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        username=current_user["username"],
        email=current_user["email"]
    )
