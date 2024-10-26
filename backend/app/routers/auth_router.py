import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from ..database import get_db
from ..models import User, AuthSession
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
logger = logging.getLogger(__name__)

class LoginRequest(BaseModel):
    username: str
    password: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

@router.post("/register")
async def register(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check if user exists
        stmt = select(User).where(
            or_(
                User.email == form_data.username,
                User.username == form_data.username
            )
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered"
            )

        # Create new user
        hashed_password = pwd_context.hash(form_data.password)
        new_user = User(
            username=form_data.username,
            email=form_data.username,  # Using username field for email
            password_hash=hashed_password
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Create access token
        access_token, expire = create_access_token(
            data={"user_id": new_user.id}
        )

        # Create auth session
        session_id = f"session_{new_user.id}_{access_token[-10:]}"
        auth_session = AuthSession(
            id=session_id,
            user_id=new_user.id,
            expires_at=expire
        )
        db.add(auth_session)
        await db.commit()

        # Set cookie
        response.set_cookie(
            key="auth_session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            expires=expire.timestamp()
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": new_user.id,
            "username": new_user.username,
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not complete registration"
        )

@router.post("/login")
async def login(
    response: Response,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Find user
        stmt = select(User).where(
            or_(
                User.email == login_data.username,
                User.username == login_data.username
            )
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not pwd_context.verify(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )

        # Create access token
        access_token, expire = create_access_token(
            data={"user_id": user.id}
        )

        # Create auth session
        session_id = f"session_{user.id}_{access_token[-10:]}"
        auth_session = AuthSession(
            id=session_id,
            user_id=user.id,
            expires_at=expire
        )
        db.add(auth_session)
        await db.commit()

        # Set cookie
        response.set_cookie(
            key="auth_session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            expires=expire.timestamp()
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not complete login"
        )

@router.post("/refresh")
async def refresh_token(
    response: Response,
    auth_session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not auth_session_id:
        raise HTTPException(
            status_code=401,
            detail="No authentication session"
        )

    try:
        # Find auth session
        stmt = select(AuthSession).where(AuthSession.id == auth_session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication session"
            )

        # Check if session is expired
        if session.expires_at < datetime.utcnow():
            await db.delete(session)
            await db.commit()
            raise HTTPException(
                status_code=401,
                detail="Session expired"
            )

        # Create new access token
        access_token, expire = create_access_token(
            data={"user_id": session.user_id}
        )

        # Update session expiry
        session.expires_at = expire
        await db.commit()

        # Set new cookie
        response.set_cookie(
            key="auth_session_id",
            value=auth_session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            expires=expire.timestamp()
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout(
    response: Response,
    auth_session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if auth_session_id:
        try:
            stmt = select(AuthSession).where(AuthSession.id == auth_session_id)
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                await db.delete(session)
                await db.commit()
        except Exception as e:
            logger.error(f"Error during logout: {e}")

    response.delete_cookie(
        key="auth_session_id",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}
