import os
import sys

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print("Files in the current directory:")
for file in os.listdir():
    print(f"- {file}")

try:
    import uvicorn
    print("uvicorn is installed")
except ImportError:
    print("uvicorn is not installed")

try:
    from app.main import app
    print("app.main.app imported successfully")
except ImportError as e:
    print(f"Error importing app.main.app: {e}")

print("Script executed successfully")
