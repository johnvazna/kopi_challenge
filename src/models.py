from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    """Model for chat requests"""
    conversation_id: Optional[str] = Field(
        None, 
        description="Existing conversation ID. If not provided, a new conversation will be started",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"}
    )
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="User message to start or continue the debate",
        json_schema_extra={"example": "Hello, let's start debating about pineapple on pizza!"}
    )
    
    @field_validator('message')
    @classmethod
    def validate_message_not_whitespace(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or only whitespace')
        return v.strip()

class ChatMessage(BaseModel):
    """Model for individual conversation message"""
    role: str = Field(..., description="Role of the message sender", json_schema_extra={"example": "user"})
    message: str = Field(..., description="Message content", json_schema_extra={"example": "I think pineapple doesn't belong on pizza"})

class ChatResponse(BaseModel):
    """Model for chat responses"""
    conversation_id: str = Field(..., description="Unique conversation identifier", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    message: List[ChatMessage] = Field(..., description="List of recent messages in the conversation")

class ConversationHistory(BaseModel):
    """Model for complete conversation history"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    messages: List[ChatMessage] = Field(..., description="Complete list of messages")
    total_messages: int = Field(..., description="Total number of messages in the conversation")
    topic: Optional[str] = Field(None, description="Debate topic for this conversation")
    stance: Optional[str] = Field(None, description="Bot's stance on the topic")
    created_at: Optional[str] = Field(None, description="Conversation creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    config: dict = Field(..., description="Configuration settings")

class PersonalityResponse(BaseModel):
    """Model for personality endpoint response"""
    personality: str = Field(..., description="Type of personality", json_schema_extra={"example": "debate-focused"})
    description: str = Field(..., description="Detailed personality description")
    current_topic: str = Field(..., description="Current debate topic")
    position: str = Field(..., description="Bot's stance on the topic")
    config: dict = Field(..., description="Configuration settings")
    message: str = Field(..., description="Additional information about the bot")

class HealthResponse(BaseModel):
    """Model for health check response"""
    status: str = Field(..., description="Service status", json_schema_extra={"example": "healthy"})
    version: str = Field(..., description="API version", json_schema_extra={"example": "1.0.0"})

class StatsResponse(BaseModel):
    """Model for statistics endpoint response"""
    storage: dict = Field(..., description="Storage statistics")
    chatbot_personality: str = Field(..., description="Chatbot personality type")
    api_version: str = Field(..., description="API version")
    config: dict = Field(..., description="Configuration settings")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error description")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

class RootResponse(BaseModel):
    """Model for root endpoint response"""
    message: str = Field(..., description="Welcome message")
    description: str = Field(..., description="API description")
    version: str = Field(..., description="API version")
    config: dict = Field(..., description="Configuration settings")
    endpoints: dict = Field(..., description="Available endpoints")
