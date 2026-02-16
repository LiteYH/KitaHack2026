from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChartConfig(BaseModel):
    """Configuration for rendering a chart"""
    type: str = Field(..., description="Chart type (bar, line, pie, area)")
    title: str = Field(..., description="Chart title")
    data: List[Dict[str, Any]] = Field(..., description="Chart data")
    xKey: Optional[str] = Field(None, description="X-axis key for bar/line charts")
    yKey: Optional[str] = Field(None, description="Y-axis key for bar charts")
    yLabel: Optional[str] = Field(None, description="Y-axis label")
    lines: Optional[List[Dict[str, Any]]] = Field(None, description="Line configurations for line charts")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous messages in the conversation for context"
    )
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")
    user_email: Optional[str] = Field(default=None, description="User email for ROI data access")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="AI assistant response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    charts: Optional[List[ChartConfig]] = Field(default=None, description="Chart configurations to display")


class ChatStreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str
    done: bool = False
