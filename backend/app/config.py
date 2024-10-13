import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/language_tutor")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Deepgram settings
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY")

    # Auth service settings
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth_and_paywall:8080")

settings = Settings()
