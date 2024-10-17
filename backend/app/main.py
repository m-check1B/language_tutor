from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

from .routers import conversation_router
from .middleware import auth_middleware, security

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Custom middleware class
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            credentials = await security(request)
            await auth_middleware(request, credentials)
        except:
            # If authentication fails, continue without setting user info
            pass
        response = await call_next(request)
        return response

# Add custom middleware
app.add_middleware(AuthMiddleware)

# Include the routers
app.include_router(conversation_router.router, prefix="/conversation", tags=["conversation"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Tutor API"}

# Print out all registered routes for debugging
for route in app.routes:
    print(f"Route: {route.path}, Methods: {route.methods}")
