from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_router, chat_router, media_router
from .database import engine, Base
import logging
from pathlib import Path
import asyncio
import os

# Setup logging to user's home directory
log_dir = Path.home() / ".language_tutor_logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to console only for development
    ]
)

# Initialize FastAPI app
app = FastAPI(title="Language Tutor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers
app.include_router(auth_router.router, prefix="/api", tags=["Authentication"])
app.include_router(chat_router.router, prefix="/api", tags=["Chat"])
app.include_router(media_router.router, prefix="/api/media", tags=["Media"])

@app.get("/")
async def root():
    return {"message": "Language Tutor API is running"}

@app.get("/api/dev/test")
async def test_dev():
    return {
        "status": "success",
        "message": "Development environment is working",
        "features": [
            "Hot reloading enabled",
            "Database connected",
            "PM2 process management"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
