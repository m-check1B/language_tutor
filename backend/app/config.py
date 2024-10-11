import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Language Tutor API"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")  # Use "db" as the default host
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "language_tutor")
    
    # Debug print statements
    print(f"POSTGRES_USER: {POSTGRES_USER}")
    print(f"POSTGRES_SERVER: {POSTGRES_SERVER}")
    print(f"POSTGRES_PORT: {POSTGRES_PORT}")
    print(f"POSTGRES_DB: {POSTGRES_DB}")
    
    # Updated DATABASE_URL construction with error handling
    try:
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
        print(f"DATABASE_URL: {DATABASE_URL}")
    except Exception as e:
        print(f"Error constructing DATABASE_URL: {e}")
        DATABASE_URL = None

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # LiveKit settings
    LIVEKIT_API_URL: str = os.getenv("LIVEKIT_API_URL")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET")

settings = Settings()
