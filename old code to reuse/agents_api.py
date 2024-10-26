import logging
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
import jwt
import aiosqlite
from config import SECRET_KEY, ALGORITHM
from database_utils import get_db
from auth_api import oauth2_scheme, verify_auth_session

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

async def get_active_agent(db, user_id):
    try:
        async with db.execute("""
            SELECT agents.* FROM agents
            JOIN active_agent ON agents.id = active_agent.agent_id
            WHERE active_agent.user_id = ?
        """, (user_id,)) as cursor:
            agent = await cursor.fetchone()
        if agent:
            logger.info(f"Retrieved active agent for user {user_id}: {agent[1]}, Voice: {agent[5]}")
        else:
            logger.warning(f"No active agent found for user {user_id}")
        return agent
    except Exception as e:
        logger.error(f"Error getting active agent for user {user_id}: {e}", exc_info=True)
        return None

async def set_active_agent(db, user_id, agent_id):
    try:
        await db.execute("INSERT OR REPLACE INTO active_agent (user_id, agent_id) VALUES (?, ?)", (user_id, agent_id))
        await db.commit()
        logger.info(f"Set active agent {agent_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Error setting active agent: {e}", exc_info=True)

async def create_agent(db, agent_data):
    try:
        await db.execute("""
            INSERT INTO agents (name, system_prompt, provider, model, voice, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, role, connections, tools) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent_data['name'], agent_data['system_prompt'], agent_data['provider'], agent_data['model'], agent_data['voice'], agent_data['temperature'], agent_data['max_tokens'], agent_data['top_p'], agent_data['frequency_penalty'], agent_data['presence_penalty'], agent_data['role'], agent_data['connections'], agent_data['tools']))
        await db.commit()
        logger.info(f"Created new agent: {agent_data['name']}, Voice: {agent_data['voice']}")
    except Exception as e:
        logger.error(f"Error creating agent: {e}", exc_info=True)

async def update_agent(db, agent_data):
    try:
        await db.execute("""
            UPDATE agents 
            SET system_prompt = ?, provider = ?, model = ?, voice = ?, temperature = ?, max_tokens = ?, top_p = ?, frequency_penalty = ?, presence_penalty = ?, role = ?, connections = ?, tools = ?
            WHERE name = ?
        """, (agent_data['system_prompt'], agent_data['provider'], agent_data['model'], agent_data['voice'], agent_data['temperature'], agent_data['max_tokens'], agent_data['top_p'], agent_data['frequency_penalty'], agent_data['presence_penalty'], agent_data['role'], agent_data['connections'], agent_data['tools'], agent_data['name']))
        await db.commit()
        logger.info(f"Updated agent: {agent_data['name']}, Voice: {agent_data['voice']}")
    except Exception as e:
        logger.error(f"Error updating agent: {e}", exc_info=True)

async def delete_agent(db, agent_name):
    try:
        await db.execute("DELETE FROM agents WHERE name = ?", (agent_name,))
        await db.commit()
        logger.info(f"Deleted agent: {agent_name}")
    except Exception as e:
        logger.error(f"Error deleting agent: {e}", exc_info=True)

async def get_agents(db: aiosqlite.Connection):
    try:
        async with db.execute("""
            SELECT id, name, system_prompt, provider, model, voice, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, role, connections, tools 
            FROM agents
        """) as cursor:
            agents = await cursor.fetchall()
        
        columns = ['id', 'name', 'system_prompt', 'provider', 'model', 'voice', 'temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty', 'role', 'connections', 'tools']
        agent_list = [dict(zip(columns, agent)) for agent in agents]
        
        for agent in agent_list:
            logger.info(f"Fetched agent: {agent['name']}, Voice: {agent['voice']}")
        
        return agent_list
    except Exception as e:
        logger.error(f"Error fetching agents: {e}", exc_info=True)
        raise

@router.post("/api/agents/create/")
async def create_agent_endpoint(request: Request, agent: AgentCreate, db = Depends(get_db)):
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

        async with db as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT id FROM agents WHERE name = ?", (agent.name,))
            if await cur.fetchone():
                raise HTTPException(status_code=400, detail="Agent with this name already exists")

        await create_agent(db, agent.dict())

        async with db as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT last_insert_rowid()")
            agent_id = (await cur.fetchone())[0]

        await set_active_agent(db, user_id, agent_id)
        return {"message": "Agent created successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error in create_agent_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/api/agents/{agent_name}/update/")
async def update_agent_endpoint(request: Request, agent_name: str, agent: AgentUpdate, db = Depends(get_db)):
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

        async with db as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT id FROM agents WHERE name = ?", (agent_name,))
            row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")

        await update_agent(db, {**agent.dict(), "name": agent_name})
        return {"message": "Agent updated successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error in update_agent_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/api/agents/delete/")
async def delete_agent_endpoint(request: Request, agent: AgentSelect, db = Depends(get_db)):
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

        async with db as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT agent_id FROM active_agent WHERE user_id = ?", (user_id,))
            active_agent = await cur.fetchone()

        await delete_agent(db, agent.agent_name)

        if active_agent:
            async with db as conn:
                cur = await conn.cursor()
                await cur.execute("SELECT id FROM agents LIMIT 1")
                new_active_agent = await cur.fetchone()
            if new_active_agent:
                await set_active_agent(db, user_id, new_active_agent[0])

        return {"message": "Agent deleted successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error in delete_agent_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/api/agents/")
async def get_agents_endpoint(request: Request, db = Depends(get_db)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        agents = await get_agents(db)
        return agents
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error in get_agents_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch agents")

@router.get("/api/agents/details/{agent_name}/")
async def get_agent_details(request: Request, agent_name: str, db = Depends(get_db)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        async with db as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT * FROM agents WHERE name = ?", (agent_name,))
            row = await cur.fetchone()
        if row:
            columns = [column[0] for column in cur.description]
            agent_details = dict(zip(columns, row))
            logger.info(f"Retrieved details for agent: {agent_name}, Voice: {agent_details.get('voice')}")
            return agent_details
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error retrieving agent details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agent details")

@router.post("/api/agents/activate/")
async def activate_agent(request: Request, agent: AgentSelect, db = Depends(get_db)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")

    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth session ID")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        async with db as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT id, voice FROM agents WHERE name = ?", (agent.agent_name,))
            row = await cur.fetchone()
        if row:
            agent_id, voice = row
            await set_active_agent(db, user_id, agent_id)
            logger.info(f"Activated agent: {agent.agent_name}, Voice: {voice}")
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
