import os  # Import for os module

class Settings:
    # Database settings
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Google Auth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Backend settings
    BACKEND_SECRET_KEY = os.getenv("BACKEND_SECRET_KEY")
    SECRET_KEY = BACKEND_SECRET_KEY  # Added SECRET_KEY
    BACKEND_PORT = os.getenv("BACKEND_PORT")

    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")

    # Deepgram settings
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

    # Token expiration settings
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))  # Default to 15 minutes

    # Algorithm setting
    ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Added ALGORITHM

    # Auth service URL
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")  # Added AUTH_SERVICE_URL

    # Production Domain
    PRODUCTION_DOMAIN = os.getenv("PRODUCTION_DOMAIN")

settings = Settings()  # Instantiate the settings
