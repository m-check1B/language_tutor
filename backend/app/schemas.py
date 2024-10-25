from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Chat schemas
class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    role: str = "user"
    media_type: Optional[str] = None
    media_url: Optional[str] = None

class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    user_id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# TTS schemas
class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"
    speed: float = 1.0
    model: str = "tts-1"

class TTSVoicePreferenceBase(BaseModel):
    voice: str
    speed: float
    model: str

class TTSVoicePreferenceCreate(TTSVoicePreferenceBase):
    pass

class TTSVoicePreference(TTSVoicePreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# File processing schemas
class FileUploadResponse(BaseModel):
    text: str
    media_type: str
    media_url: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    choices: List[ChatMessage]
