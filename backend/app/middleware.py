from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import get_current_user, check_subscription_status

security = HTTPBearer()

async def auth_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    token = credentials.credentials
    user = await get_current_user(token)
    request.state.user = user
    return user

async def subscription_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    token = credentials.credentials
    user = await get_current_user(token)
    subscription = await check_subscription_status(user)
    request.state.user = user
    request.state.subscription = subscription
    return user

def auth_required(func):
    async def wrapper(request: Request, *args, **kwargs):
        await auth_middleware(request)
        return await func(request, *args, **kwargs)
    return wrapper

def subscription_required(func):
    async def wrapper(request: Request, *args, **kwargs):
        await subscription_middleware(request)
        return await func(request, *args, **kwargs)
    return wrapper
