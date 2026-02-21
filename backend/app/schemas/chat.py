from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant", "system"]
    content: str


class ConfirmationRequest(BaseModel):
    """Request for user confirmation (Human-in-the-Loop)"""
    action_type: Literal["roi_data_access", "other"] = Field(..., description="Type of action requiring confirmation")
    message: str = Field(..., description="Confirmation message to display to user")
    action_id: str = Field(..., description="Unique identifier for this action")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional context about the action")


class ConfirmationResponse(BaseModel):
    """User's response to a confirmation request"""
    action_id: str = Field(..., description="ID of the action being confirmed")
    confirmed: bool = Field(..., description="Whether user confirmed the action")
    user_email: Optional[str] = Field(default=None, description="User email for authenticated actions")


class ApprovalDecision(BaseModel):
    """User's approval decision for LangGraph HITL"""
    thread_id: str = Field(..., description="Thread ID of the conversation requiring approval")
    approved: bool = Field(..., description="Whether user approved the tool execution")
    tool_name: Optional[str] = Field(default=None, description="Name of the tool being approved")


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
    message: str = Field(default="", max_length=5000, description="User message (can be empty when approval_decision is provided)")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Previous messages in the conversation for context"
    )
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")
    user_email: Optional[str] = Field(default=None, description="User email for ROI data access")
    confirmation_response: Optional[ConfirmationResponse] = Field(
        default=None, 
        description="User's response to a pending confirmation request (HITL)"
    )
    thread_id: Optional[str] = Field(default=None, description="Thread ID for resuming conversations with state")
    approval_decision: Optional[ApprovalDecision] = Field(
        default=None,
        description="User's approval decision for LangGraph HITL"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="AI assistant response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    charts: Optional[List[ChartConfig]] = Field(default=None, description="Chart configurations to display")
    requires_confirmation: bool = Field(default=False, description="Whether this response requires user confirmation")
    confirmation_request: Optional[ConfirmationRequest] = Field(default=None, description="Confirmation request details")
    requires_approval: bool = Field(default=False, description="Whether this response requires user approval (LangGraph HITL)")
    approval_request: Optional[Dict[str, Any]] = Field(default=None, description="Approval request details for LangGraph HITL")
    thread_id: Optional[str] = Field(default=None, description="Thread ID for stateful conversations")


class ChatStreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str
    done: bool = False
