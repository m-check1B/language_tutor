import logging
from datetime import datetime
from typing import AsyncGenerator, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
from .config import DATABASE_URL
from .models import Base, User, Agent, ActiveAgent, ChatSession, ChatMessage, AuthSession

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session maker
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Initialize the database"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

# Database utility functions
async def create_chat_session(db: AsyncSession, user_id: int) -> Optional[int]:
    """Create a new chat session"""
    try:
        chat_session = ChatSession(user_id=user_id)
        db.add(chat_session)
        await db.commit()
        await db.refresh(chat_session)
        return chat_session.id
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        await db.rollback()
        return None

async def end_chat_session(db: AsyncSession, session_id: int):
    """End a chat session"""
    try:
        stmt = (
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(end_time=datetime.utcnow())
        )
        await db.execute(stmt)
        await db.commit()
    except Exception as e:
        logger.error(f"Error ending chat session: {e}")
        await db.rollback()

async def update_and_get_history(
    db: AsyncSession,
    user_id: int,
    message: str,
    response: str,
    chat_session_id: int,
    audio_url: Optional[str] = None
) -> List[Tuple]:
    """Update chat history and return the updated history"""
    try:
        # Add new message
        chat_message = ChatMessage(
            chat_session_id=chat_session_id,
            user_id=user_id,
            content=message,
            response=response,
            audio_url=audio_url
        )
        db.add(chat_message)
        await db.commit()

        # Get updated history
        stmt = select(ChatMessage).where(
            ChatMessage.chat_session_id == chat_session_id
        ).order_by(ChatMessage.created_at)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return [
            (msg.content, msg.response, msg.audio_url, msg.created_at)
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error updating chat history: {e}")
        await db.rollback()
        return []

async def get_chat_history(
    db: AsyncSession,
    user_id: int,
    chat_session_id: int
) -> List[Tuple]:
    """Get chat history for a session"""
    try:
        stmt = select(ChatMessage).where(
            ChatMessage.chat_session_id == chat_session_id,
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.created_at)
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return [
            (msg.content, msg.response, msg.audio_url, msg.created_at)
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return []

async def get_active_agent(db: AsyncSession, user_id: int) -> Optional[Agent]:
    """Get active agent for user"""
    try:
        stmt = select(Agent).join(ActiveAgent).where(ActiveAgent.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting active agent: {e}")
        return None

async def set_active_agent(db: AsyncSession, user_id: int, agent_id: int):
    """Set active agent for user"""
    try:
        # Check if user already has an active agent
        stmt = select(ActiveAgent).where(ActiveAgent.user_id == user_id)
        result = await db.execute(stmt)
        active_agent = result.scalar_one_or_none()

        if active_agent:
            active_agent.agent_id = agent_id
            active_agent.activated_at = datetime.utcnow()
        else:
            active_agent = ActiveAgent(user_id=user_id, agent_id=agent_id)
            db.add(active_agent)

        await db.commit()
    except Exception as e:
        logger.error(f"Error setting active agent: {e}")
        await db.rollback()

async def verify_auth_session(db: AsyncSession, session_id: str) -> bool:
    """Verify if an authentication session is valid"""
    try:
        stmt = select(AuthSession).where(AuthSession.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            return False

        if session.expires_at < datetime.utcnow():
            await db.delete(session)
            await db.commit()
            return False

        return True
    except Exception as e:
        logger.error(f"Error verifying auth session: {e}")
        return False
