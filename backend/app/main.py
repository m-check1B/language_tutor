from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from .routers import conversation_router
from .middleware import auth_middleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers
app.include_router(conversation_router.router, prefix="/conversation", tags=["conversation"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Tutor API"}

# Add global middleware
app.middleware("http")(auth_middleware)

# Print out all registered routes for debugging
for route in app.routes:
    print(f"Route: {route.path}, Methods: {route.methods}")
