import jwt
from datetime import datetime, timedelta

def generate_test_token():
    # Create a fake payload
    payload = {
        "sub": "testuser@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "is_active": True,
        "is_subscribed": True
    }
    
    # Use a fake secret key
    fake_secret_key = "fake_secret_key_for_testing"
    
    # Generate the token
    token = jwt.encode(payload, fake_secret_key, algorithm="HS256")
    print(f"Generated fake test token: {token}")
    return token

if __name__ == "__main__":
    generate_test_token()
