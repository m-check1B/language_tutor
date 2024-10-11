import os
import requests
import websocket
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PRODUCTION_DOMAIN = os.getenv('PRODUCTION_DOMAIN')
FRONTEND_URL = f"http://{PRODUCTION_DOMAIN}:3000"
BACKEND_URL = f"http://{PRODUCTION_DOMAIN}:8000"
API_BASE_URL = f"{BACKEND_URL}/api"
WS_URL = f"ws://{PRODUCTION_DOMAIN}:8000/ws"

def test_frontend():
    response = requests.get(FRONTEND_URL)
    assert response.status_code == 200, "Frontend connection failed"
    print("Frontend connection successful")

def test_api_endpoints():
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

def test_websocket():
    ws = websocket.create_connection(WS_URL)
    ws.send(json.dumps({"type": "test"}))
    result = ws.recv()
    assert result, "WebSocket connection failed"
    print("WebSocket connection successful")
    ws.close()

if __name__ == "__main__":
    try:
        test_frontend()
        test_api_endpoints()
        test_websocket()
        print("All production tests passed successfully!")
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
