from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.models import Base, engine, get_db
from app.config import settings
from app.routers import auth_router, conversation_router
from app.websocket_handler import websocket_endpoint
from app.livekit_handler import router as livekit_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow the frontend to access the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Language Tutor API"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    try:
        # Try to query something from the database
        db.execute("SELECT 1")
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {str(e)}"}

# Include the authentication router
app.include_router(auth_router.router, prefix="/auth", tags=["authentication"])

# Include the conversation router
app.include_router(conversation_router.router, prefix="/api", tags=["conversations"])

# Include the LiveKit router
app.include_router(livekit_router, prefix="/livekit", tags=["livekit"])

# WebSocket route
@app.websocket("/ws/{token}")
async def websocket_route(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    try:
        await websocket_endpoint(websocket, token, db)
    except WebSocketDisconnect:
        pass

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        routes=app.routes,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
