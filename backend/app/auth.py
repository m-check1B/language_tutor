import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import aiosqlite
import uuid
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SESSION_EXPIRE_DAYS
from .database import get_db

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

async def create_auth_session(db: aiosqlite.Connection, user_id: int) -> str:
    """Create a new authentication session"""
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRE_DAYS)
    
    try:
        await db.execute(
            "INSERT INTO auth_sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
            (session_id, user_id, expires_at)
        )
        await db.commit()
        return session_id
    except Exception as e:
        logger.error(f"Error creating auth session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create authentication session"
        )

async def verify_auth_session(db: aiosqlite.Connection, session_id: str) -> bool:
    """Verify if an authentication session is valid"""
    try:
        async with db.execute(
            """
            SELECT user_id, expires_at 
            FROM auth_sessions 
            WHERE id = ?
            """,
            (session_id,)
        ) as cursor:
            result = await cursor.fetchone()
            
            if not result:
                return False
                
            expires_at = datetime.fromisoformat(result[1])
            if expires_at < datetime.utcnow():
                await db.execute("DELETE FROM auth_sessions WHERE id = ?", (session_id,))
                await db.commit()
                return False
                
            return True
    except Exception as e:
        logger.error(f"Error verifying auth session: {e}")
        return False

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: aiosqlite.Connection = Depends(get_db)):
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
        async with db.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,)
        ) as cursor:
            user = await cursor.fetchone()
            
        if user is None:
            raise credentials_exception
            
        return {"id": user[0], "username": user[1], "email": user[2]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise credentials_exception

async def authenticate_user(db: aiosqlite.Connection, username: str, password: str):
    """Authenticate a user"""
    try:
        async with db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        ) as cursor:
            user = await cursor.fetchone()
            
        if not user or not verify_password(password, user[2]):
            return False
            
        return {"id": user[0], "username": user[1]}
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return False

async def register_user(db: aiosqlite.Connection, username: str, email: str, password: str):
    """Register a new user"""
    try:
        # Check if username or email already exists
        async with db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ) as cursor:
            if await cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )
        
        # Create new user
        password_hash = get_password_hash(password)
        async with db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        ) as cursor:
            await db.commit()
            return {"id": cursor.lastrowid, "username": username, "email": email}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user"
        )

async def end_auth_session(db: aiosqlite.Connection, session_id: str):
    """End an authentication session"""
    try:
        await db.execute("DELETE FROM auth_sessions WHERE id = ?", (session_id,))
        await db.commit()
    except Exception as e:
        logger.error(f"Error ending auth session: {e}")
