from fastapi import FastAPI
from dotenv import load_dotenv  # Import for loading environment variables
import os

load_dotenv()  # Load environment variables from .env file

from .routers import auth_router, conversation_router  # Adjusted imports

app = FastAPI()

# Include the routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(conversation_router, prefix="/conversation", tags=["conversation"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Tutor API"}
