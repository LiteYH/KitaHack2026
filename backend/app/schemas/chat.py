from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


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


class CampaignDataAttachment(BaseModel):
    """Campaign data to be displayed in chat"""
    type: Literal["analytics", "edit_request"] = "analytics"
    campaigns: List[Dict[str, Any]]
    metrics: List[Dict[str, Any]]
    summary: Dict[str, Any]
    intent: Dict[str, Any]
    show_visualization: bool = Field(default=False, description="Whether to show visualization prompt")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="AI assistant response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    campaign_data: Optional[CampaignDataAttachment] = Field(
        default=None, 
        description="Structured campaign data for UI rendering"
    )


class ChatStreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str
    done: bool = False
