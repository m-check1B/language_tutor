from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os

security = HTTPBearer(auto_error=False)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_paywall_api:8000")

async def verify_token(token: str):
    # For development, return a mock user
    return {"id": "mock_user_id", "email": "mock@example.com"}

async def check_subscription(user_id: str):
    # For development, return a mock subscription
    return {"is_active": True}

async def auth_middleware(request: Request, credentials: HTTPAuthorizationCredentials = None):
    if credentials is None:
        # For development, set a mock user
        request.state.user = {"id": "mock_user_id", "email": "mock@example.com"}
        return request.state.user
    token = credentials.credentials
    user = await verify_token(token)
    request.state.user = user
    return user

async def subscription_middleware(request: Request, credentials: HTTPAuthorizationCredentials = None):
    if credentials is None:
        # For development, set a mock user and subscription
        request.state.user = {"id": "mock_user_id", "email": "mock@example.com"}
        request.state.subscription = {"is_active": True}
        return request.state.user
    token = credentials.credentials
    user = await verify_token(token)
    subscription = await check_subscription(user["id"])
    request.state.user = user
    request.state.subscription = subscription
    return user

def auth_required(func):
    async def wrapper(request: Request, *args, **kwargs):
        credentials = await security(request)
        await auth_middleware(request, credentials)
        return await func(request, *args, **kwargs)
    return wrapper

def subscription_required(func):
    async def wrapper(request: Request, *args, **kwargs):
        credentials = await security(request)
        await subscription_middleware(request, credentials)
        if not request.state.subscription["is_active"]:
            raise HTTPException(status_code=403, detail="Active subscription required")
        return await func(request, *args, **kwargs)
    return wrapper
