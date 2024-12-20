import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import agents_router, multimedia_router, ws_router, auth_router, chat_router
from .database import init_db
from .config import (
    CORS_SETTINGS,
    LOG_LEVEL,
    LOG_FORMAT,
    ENABLE_AUDIO,
    ENABLE_VIDEO,
    ENABLE_IMAGE,
    ENABLE_PDF,
    ENABLE_WEBSOCKET,
    ENABLE_TTS,
    CORS_ORIGINS
)

# Configure logging to console
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Language Tutor API")

# Configure CORS with credentials support
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth_router.router, tags=["Authentication"])
app.include_router(agents_router.router, tags=["Agents"])
app.include_router(multimedia_router.router, tags=["Multimedia"])
app.include_router(chat_router.router, tags=["Chat"])
if ENABLE_WEBSOCKET:
    app.include_router(ws_router.router, tags=["WebSocket"])

@app.on_event("startup")
async def startup_event():
    """Initialize the database and other startup tasks"""
    try:
        await init_db()
        logger.info("Database initialized successfully")

        # Log enabled features
        features = {
            "Audio": ENABLE_AUDIO,
            "Video": ENABLE_VIDEO,
            "Image": ENABLE_IMAGE,
            "PDF": ENABLE_PDF,
            "WebSocket": ENABLE_WEBSOCKET,
            "Text-to-Speech": ENABLE_TTS
        }
        logger.info("Enabled features: %s", 
            ", ".join(f"{k}: {v}" for k, v in features.items())
        )

        # Log CORS settings
        logger.info("CORS Origins: %s", CORS_ORIGINS)
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Handle authentication and token refresh"""
    try:
        response = await call_next(request)
        
        # Check if response indicates token expiration
        if response.status_code == 401:
            # Let the client handle token refresh
            response.headers["X-Token-Expired"] = "true"
        
        return response
    except Exception as e:
        logger.error(f"Auth middleware error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for API health check"""
    return {
        "status": "ok",
        "message": "Language Tutor API is running",
        "features": {
            "audio": ENABLE_AUDIO,
            "video": ENABLE_VIDEO,
            "image": ENABLE_IMAGE,
            "pdf": ENABLE_PDF,
            "websocket": ENABLE_WEBSOCKET,
            "tts": ENABLE_TTS
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
