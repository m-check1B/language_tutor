from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_paywall_api:8000")

async def verify_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/api/auth/verify-token", json={"token": token})
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

async def check_subscription(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AUTH_SERVICE_URL}/api/subscription/status/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=401, detail="Unable to check subscription status")

async def auth_middleware(request: Request, credentials: HTTPAuthorizationCredentials = None):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    token = credentials.credentials
    user = await verify_token(token)
    request.state.user = user
    return user

async def subscription_middleware(request: Request, credentials: HTTPAuthorizationCredentials = None):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
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
