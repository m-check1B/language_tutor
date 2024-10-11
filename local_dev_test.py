import os
import requests
import websocket
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FRONTEND_URL = "http://localhost:5175"
BACKEND_URL = "http://localhost:8000"
API_BASE_URL = f"{BACKEND_URL}/api"
WS_URL = "ws://localhost:8000/ws"

def test_frontend():
    try:
        response = requests.get(FRONTEND_URL)
        assert response.status_code == 200, "Frontend connection failed"
        print("Frontend connection successful")
    except requests.ConnectionError:
        print("Frontend connection failed. Make sure the frontend server is running on port 5175.")

def test_api_endpoints():
    try:
        # Test registration
        register_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data)
        assert response.status_code == 200, "Registration failed"
        print("Registration successful")

        # Test login
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = requests.post(f"{API_BASE_URL}/auth/token", data=login_data)
        assert response.status_code == 200, "Login failed"
        token = response.json()["access_token"]
        print("Login successful")

        # Test creating a conversation
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE_URL}/conversations", headers=headers)
        assert response.status_code == 200, "Creating conversation failed"
        conversation_id = response.json()["id"]
        print("Creating conversation successful")

        # Test sending a message
        message_data = {"content": "Hello, AI!"}
        response = requests.post(f"{API_BASE_URL}/conversations/{conversation_id}/messages", headers=headers, json=message_data)
        assert response.status_code == 200, "Sending message failed"
        print("Sending message successful")
    except requests.ConnectionError:
        print("Backend connection failed. Make sure the backend server is running on port 8000.")

def test_websocket():
    try:
        ws = websocket.create_connection(WS_URL)
        ws.send(json.dumps({"type": "test"}))
        result = ws.recv()
        assert result, "WebSocket connection failed"
        print("WebSocket connection successful")
        ws.close()
    except Exception as e:
        print(f"WebSocket connection failed: {str(e)}")

if __name__ == "__main__":
    print("Starting local development tests...")
    test_frontend()
    test_api_endpoints()
    test_websocket()
    print("Local development tests completed.")
