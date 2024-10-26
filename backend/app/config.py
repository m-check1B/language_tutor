import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database settings
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "language_tutor")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Construct database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))  # Changed to 8001 to match frontend expectations

# CORS settings
# Include both HTTP and WebSocket origins
http_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
ws_origins = ["ws://localhost:5173", "ws://127.0.0.1:5173"]
CORS_ORIGINS = os.getenv("CORS_ORIGINS", ",".join(http_origins + ws_origins)).split(",")

CORS_SETTINGS = {
    "allow_origins": CORS_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Token-Expired"]
}

# Feature flags
ENABLE_AUDIO = os.getenv("ENABLE_AUDIO", "true").lower() == "true"
ENABLE_VIDEO = os.getenv("ENABLE_VIDEO", "true").lower() == "true"
ENABLE_IMAGE = os.getenv("ENABLE_IMAGE", "true").lower() == "true"
ENABLE_PDF = os.getenv("ENABLE_PDF", "true").lower() == "true"
ENABLE_WEBSOCKET = os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"
ENABLE_TTS = os.getenv("ENABLE_TTS", "true").lower() == "true"

# LLM settings
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P", "1.0"))
DEFAULT_FREQUENCY_PENALTY = float(os.getenv("DEFAULT_FREQUENCY_PENALTY", "0.0"))
DEFAULT_PRESENCE_PENALTY = float(os.getenv("DEFAULT_PRESENCE_PENALTY", "0.0"))

# Agent settings
DEFAULT_AGENT_PROVIDER = os.getenv("DEFAULT_AGENT_PROVIDER", "openai")
DEFAULT_AGENT_MODEL = os.getenv("DEFAULT_AGENT_MODEL", "gpt-4o-mini")
DEFAULT_AGENT_VOICE = os.getenv("DEFAULT_AGENT_VOICE", "alloy")

# TTS settings
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "alloy")
DEFAULT_SPEECH_MODEL = os.getenv("DEFAULT_SPEECH_MODEL", "tts-1")
AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Session settings
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "auth_session_id")
SESSION_EXPIRE_DAYS = int(os.getenv("SESSION_EXPIRE_DAYS", "7"))

# Upload settings
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))  # 10MB default
ALLOWED_EXTENSIONS = {
    'audio': {'wav', 'mp3', 'ogg', 'webm'},
    'video': {'mp4', 'webm', 'avi'},
    'image': {'jpg', 'jpeg', 'png', 'gif'},
    'document': {'txt', 'pdf', 'doc', 'docx'}
}

# WebSocket settings
WS_HEARTBEAT_INTERVAL = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
WS_RECONNECT_INTERVAL = int(os.getenv("WS_RECONNECT_INTERVAL", "5"))
WS_MAX_RECONNECT_ATTEMPTS = int(os.getenv("WS_MAX_RECONNECT_ATTEMPTS", "5"))

# System prompts
DEFAULT_SYSTEM_PROMPT = os.getenv("DEFAULT_SYSTEM_PROMPT", """You are a highly skilled and patient language tutor. Your role is to:

1. Help users improve their language skills through natural conversation
2. Correct grammar and pronunciation mistakes gently and constructively
3. Explain language concepts clearly and provide relevant examples
4. Adapt your teaching style to the user's proficiency level
5. Encourage and motivate users to practice and improve
6. Provide cultural context when relevant to language learning
7. Suggest exercises and activities appropriate to the user's level
8. Help with vocabulary building and idiomatic expressions
9. Give feedback that is both specific and encouraging
10. Maintain a supportive and engaging learning environment

Remember to:
- Be patient and encouraging
- Provide clear explanations
- Use examples that are relevant to real-life situations
- Adjust your language level to match the user's proficiency
- Celebrate progress and provide constructive feedback
- Keep the conversation engaging and interactive""")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs/app.log"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Agent providers
AVAILABLE_PROVIDERS = {
    "openai": {
        "models": ["gpt-4o-mini", "gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
        "api_key": OPENAI_API_KEY
    },
    "anthropic": {
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-2.1"],
        "api_key": ANTHROPIC_API_KEY
    }
}

# Default provider and model if not specified
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
if DEFAULT_PROVIDER not in AVAILABLE_PROVIDERS:
    DEFAULT_PROVIDER = "openai"

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
if DEFAULT_MODEL not in AVAILABLE_PROVIDERS[DEFAULT_PROVIDER]["models"]:
    DEFAULT_MODEL = "gpt-4o-mini"

# Validate required settings
def validate_settings():
    required_settings = {
        "DATABASE_URL": DATABASE_URL,
        "SECRET_KEY": SECRET_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "DEEPGRAM_API_KEY": DEEPGRAM_API_KEY,
    }

    missing_settings = [key for key, value in required_settings.items() if not value]
    
    if missing_settings:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_settings)}"
        )

# Run validation on startup
validate_settings()
