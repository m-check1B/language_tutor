import logging
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
import jwt
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import SECRET_KEY, ALGORITHM
from ..database import get_db
from ..auth import verify_auth_session
from ..models import Agent, ActiveAgent

router = APIRouter()
logger = logging.getLogger(__name__)

class AgentCreate(BaseModel):
    name: str
    system_prompt: str
    provider: str
    model: str
    voice: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1000, ge=1)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    role: Optional[str] = None
    connections: Optional[str] = None
    tools: Optional[str] = None

class AgentSelect(BaseModel):
    agent_name: str

class AgentUpdate(BaseModel):
    system_prompt: str
    provider: str
    model: str
    voice: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1000, ge=1)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    role: Optional[str] = None
    connections: Optional[str] = None
    tools: Optional[str] = None

async def get_active_agent(db: AsyncSession, user_id: int):
    try:
        stmt = (
            select(Agent)
            .join(ActiveAgent)
            .where(ActiveAgent.user_id == user_id)
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if agent:
            logger.info(f"Retrieved active agent for user {user_id}: {agent.name}, Voice: {agent.voice}")
        else:
            logger.warning(f"No active agent found for user {user_id}")
        return agent
    except Exception as e:
        logger.error(f"Error getting active agent for user {user_id}: {e}", exc_info=True)
        return None

async def set_active_agent(db: AsyncSession, user_id: int, agent_id: int):
    try:
        stmt = (
            update(ActiveAgent)
            .where(ActiveAgent.user_id == user_id)
            .values(agent_id=agent_id)
        )
        result = await db.execute(stmt)
        if result.rowcount == 0:
            # If no existing record was updated, insert a new one
            stmt = insert(ActiveAgent).values(user_id=user_id, agent_id=agent_id)
            await db.execute(stmt)
        await db.commit()
        logger.info(f"Set active agent {agent_id} for user {user_id}")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error setting active agent: {e}", exc_info=True)
        raise

@router.post("/api/agents/create/")
async def create_agent_endpoint(
    request: Request,
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Check if agent with same name exists
        stmt = select(Agent).where(Agent.name == agent.name)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Agent with this name already exists")

        # Create new agent
        new_agent = Agent(
            name=agent.name,
            system_prompt=agent.system_prompt,
            provider=agent.provider,
            model=agent.model,
            voice=agent.voice,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
            top_p=agent.top_p,
            frequency_penalty=agent.frequency_penalty,
            presence_penalty=agent.presence_penalty,
            role=agent.role,
            connections=agent.connections,
            tools=agent.tools
        )
        db.add(new_agent)
        await db.commit()
        await db.refresh(new_agent)

        # Set as active agent
        await set_active_agent(db, user_id, new_agent.id)
        return {"message": "Agent created successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in create_agent_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/api/agents/")
async def get_agents_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        stmt = select(Agent)
        result = await db.execute(stmt)
        agents = result.scalars().all()
        
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "system_prompt": agent.system_prompt,
                "provider": agent.provider,
                "model": agent.model,
                "voice": agent.voice,
                "temperature": agent.temperature,
                "max_tokens": agent.max_tokens,
                "top_p": agent.top_p,
                "frequency_penalty": agent.frequency_penalty,
                "presence_penalty": agent.presence_penalty,
                "role": agent.role,
                "connections": agent.connections,
                "tools": agent.tools
            }
            for agent in agents
        ]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error in get_agents_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch agents")

@router.post("/api/agents/activate/")
async def activate_agent(
    request: Request,
    agent: AgentSelect,
    db: AsyncSession = Depends(get_db)
):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        stmt = select(Agent).where(Agent.name == agent.agent_name)
        result = await db.execute(stmt)
        db_agent = result.scalar_one_or_none()
        
        if db_agent:
            await set_active_agent(db, user_id, db_agent.id)
            logger.info(f"Activated agent: {agent.agent_name}, Voice: {db_agent.voice}")
            return {"message": "Agent activated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error activating agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to activate agent")
