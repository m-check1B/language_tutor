from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "language_tutor"

    # JWT settings
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # Deepgram settings
    DEEPGRAM_API_KEY: str = ""

    # Auth service settings
    AUTH_SERVICE_URL: str = "http://auth-service:8000"

    class Config:
        env_file = ".env"

settings = Settings()
