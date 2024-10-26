import os
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional, Dict, List
import jwt
from google.oauth2 import service_account
import openai
import vertexai
from dotenv import load_dotenv

from auth_api import (
    router as auth_router,
    get_current_user,
    create_access_token,
    get_db as get_db_auth
)
from agents_api import router as agents_router
from projects_api import router as projects_router
from tools_api import router as tools_router
from database_utils import (
    create_table, get_db,
    clean_expired_auth_sessions
)
from task_scheduler import TaskScheduler
from rabbitmq_handler import rabbitmq_handler_instance, InterAgentRouter
from multimedia_api import router as multimedia_router  # Import the multimedia router
from ws_api import router as ws_router  # Import the websocket router
from frontend_errors_api import router as frontend_errors_router  # Import the frontend errors router

# Load environment variables from the .env file in the root directory
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

# Setup logging
log_file_path = "./logs/application.log"
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set timezone
TIMEZONE = os.getenv("TIMEZONE", "UTC")
os.environ['TZ'] = TIMEZONE

try:
    import pytz
    pytz.timezone(TIMEZONE)
except Exception as e:
    logger.error(f"Timezone setting error: {e}")
    TIMEZONE = "UTC"
    os.environ['TZ'] = TIMEZONE

# Access environment variables
ORIGINS = os.getenv("ORIGINS", "*")
BACKENDHOST = os.getenv("BACKENDHOST", "0.0.0.0")
BACKENDPORT = int(os.getenv("BACKENDPORT", 8000))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
MODEL_ID = os.getenv("MODEL_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_ID = os.getenv("GROQ_MODEL_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

# Initialize API clients and models
credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)
openai.api_key = OPENAI_API_KEY

# Initialize the TaskScheduler
scheduler = TaskScheduler()
scheduler.start()

# Initialize FastAPI application
app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")  # Detailed error logging
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.on_event("startup")
async def startup_event():
    await create_table()
    await rabbitmq_handler_instance.connect()
    inter_agent_router = InterAgentRouter(rabbitmq_handler_instance)

@app.on_event("shutdown")
async def shutdown_event():
    await rabbitmq_handler_instance.close()

# Import routers
app.include_router(auth_router, tags=["auth"])
app.include_router(agents_router, tags=["agents"])
app.include_router(projects_router, tags=["projects"])
app.include_router(tools_router, tags=["tools"])
app.include_router(multimedia_router, tags=["multimedia"])
app.include_router(ws_router, tags=["websocket"])
app.include_router(frontend_errors_router, tags=["frontend_errors"])  # Include the frontend errors router

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/main/test")
async def test_endpoint():
    return {"message": "Test successful"}

@app.get("/api/auth/status")
async def auth_status(request: Request):
    auth_session_id = request.cookies.get("auth_session_id")
    if not auth_session_id:
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    async with get_db_auth() as conn:
        session_valid = await verify_auth_session(conn, auth_session_id)
        if session_valid:
            return {"isAuthenticated": True}
    return JSONResponse(status_code=401, content={"message": "Not authenticated"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=BACKENDHOST,
        port=BACKENDPORT,
        ssl_keyfile="/etc/nginx/ssl/jackwolf_dev_copy.key",
        ssl_certfile="/etc/nginx/ssl/jackwolf_dev_combined.pem"
    )
