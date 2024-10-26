from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    auth_sessions = relationship("AuthSession", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    active_agent = relationship("ActiveAgent", back_populates="user", uselist=False)

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    system_prompt = Column(Text, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    voice = Column(String)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    top_p = Column(Float, default=1.0)
    frequency_penalty = Column(Float, default=0.0)
    presence_penalty = Column(Float, default=0.0)
    role = Column(String)
    connections = Column(String)
    tools = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    active_users = relationship("ActiveAgent", back_populates="agent")

class ActiveAgent(Base):
    __tablename__ = "active_agent"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    activated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="active_agent")
    agent = relationship("Agent", back_populates="active_users")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    response = Column(Text)
    audio_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_error = Column(Boolean, default=False)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
    user = relationship("User")

class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="auth_sessions")
