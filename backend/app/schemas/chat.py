from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous messages in the conversation for context"
    )
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="AI assistant response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")


class ChatStreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str
    done: bool = False
