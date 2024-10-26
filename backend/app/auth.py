import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, AuthSession
import jwt
from passlib.context import CryptContext
from .config import SECRET_KEY, ALGORITHM
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def register_user(db: AsyncSession, username: str, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """Register a new user"""
    try:
        # Check if username exists
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return False, "Username already exists", None

        # Check if email exists
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return False, "Email already exists", None

        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"User registered successfully: {username}")
        return True, "User registered successfully", new_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering user: {e}", exc_info=True)
        return False, f"Registration failed: {str(e)}", None

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate a user and return the user object if successful"""
    try:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {e}", exc_info=True)
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_auth_session(db: AsyncSession, session_id: str) -> bool:
    """Verify if an authentication session is valid"""
    try:
        stmt = select(AuthSession).where(AuthSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            logger.warning(f"Auth session not found: {session_id}")
            return False

        if session.expires_at < datetime.utcnow():
            await db.delete(session)
            await db.commit()
            logger.info(f"Auth session expired: {session_id}")
            return False

        logger.info(f"Auth session verified: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Error verifying auth session: {e}", exc_info=True)
        return False

async def create_auth_session(db: AsyncSession, user_id: int, session_id: str, expire_days: int = 7) -> bool:
    """Create a new authentication session"""
    try:
        expires_at = datetime.utcnow() + timedelta(days=expire_days)
        session = AuthSession(
            id=session_id,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(session)
        await db.commit()
        logger.info(f"Created auth session for user {user_id}: {session_id}")
        return True
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating auth session: {e}", exc_info=True)
        return False

async def delete_auth_session(db: AsyncSession, session_id: str) -> bool:
    """Delete an authentication session"""
    try:
        stmt = select(AuthSession).where(AuthSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            await db.delete(session)
            await db.commit()
            logger.info(f"Deleted auth session: {session_id}")
            return True
        return False
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting auth session: {e}", exc_info=True)
        return False

async def end_auth_session(db: AsyncSession, session_id: str) -> Tuple[bool, str]:
    """End an authentication session and return status and message"""
    try:
        if await delete_auth_session(db, session_id):
            return True, "Session ended successfully"
        return False, "Session not found"
    except Exception as e:
        logger.error(f"Error ending auth session: {e}", exc_info=True)
        return False, f"Error ending session: {str(e)}"

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get the current authenticated user from the request"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise credentials_exception

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing auth session ID"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

        # Verify session
        if not await verify_auth_session(db, auth_session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )

        # Get user
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
