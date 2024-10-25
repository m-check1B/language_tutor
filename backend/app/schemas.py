from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    content: Optional[str] = None
    audio_url: Optional[str] = None
    is_user_message: bool = True

class MessageCreate(MessageBase):
    conversation_id: int
    user_id: int

class Message(MessageBase):
    id: int
    created_at: datetime
    conversation_id: int
    user_id: int

    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    title: str
    is_active: bool = True

class ConversationCreate(ConversationBase):
    user_id: int

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = []

    class Config:
        from_attributes = True

# User Preference schemas
class UserPreferenceBase(BaseModel):
    language: str = "en"
    theme: str = "light"
    voice_enabled: bool = True

class UserPreferenceCreate(UserPreferenceBase):
    user_id: int

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Chat specific schemas
class ChatMessage(BaseModel):
    message: Optional[str] = None
    audio: Optional[bytes] = None

class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None
    error: Optional[str] = None

# WebSocket schemas
class WSMessage(BaseModel):
    type: str  # "text" or "audio"
    content: str
    conversation_id: Optional[int] = None

class WSResponse(BaseModel):
    type: str
    content: str
    error: Optional[str] = None
    conversation_id: Optional[int] = None
    timestamp: datetime = datetime.now()
