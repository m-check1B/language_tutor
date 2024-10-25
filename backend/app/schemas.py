from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class MessageBase(BaseModel):
    content: str
    role: str
    media_type: Optional[str] = None
    media_url: Optional[str] = None

class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"
    model: str = "tts-1"
    speed: float = 1.0

class TTSVoicePreferenceBase(BaseModel):
    voice: str
    speed: float = 1.0
    model: str = "tts-1"

class TTSVoicePreferenceCreate(TTSVoicePreferenceBase):
    pass

class TTSVoicePreference(TTSVoicePreferenceBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    text: str
    media_type: str
    media_url: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str

class WSMessage(BaseModel):
    type: str
    content: str
    conversation_id: Optional[int] = None

class WSResponse(BaseModel):
    type: str
    content: str
    conversation_id: Optional[int] = None
