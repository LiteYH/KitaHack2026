from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class AgentChatRequest(BaseModel):
    """Request model for agent chat endpoint (multi-agent system)."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    thread_id: Optional[str] = Field(default=None, description="Thread ID for conversation continuity")
    user_id: Optional[str] = Field(default=None, description="Firebase user ID")


class AgentChatResponse(BaseModel):
    """Response model for agent chat endpoint."""
    message: str = Field(..., description="AI assistant response")
    thread_id: str = Field(..., description="Thread ID for conversation continuity")
    agent: Optional[str] = Field(default=None, description="Agent that handled the request")


class HITLDecision(BaseModel):
    """HITL decision for a single interrupt"""
    type: Literal["approve", "edit", "reject"] = Field(..., description="Decision type")
    interrupt_id: Optional[str] = Field(default=None, description="ID of the interrupt being responded to")
    action: Optional[str] = Field(default=None, description="Tool action name being edited")
    args: Optional[dict] = Field(default=None, description="Edited arguments (only for 'edit' type)")
    feedback: Optional[str] = Field(default=None, description="Feedback message (for 'reject' type)")


class AgentResumeRequest(BaseModel):
    """Request to resume an interrupted agent execution"""
    agent_name: str = Field(..., description="Name of the agent to resume (e.g., 'competitor_monitoring')")
    thread_id: str = Field(..., description="Thread ID of the interrupted execution")
    decisions: List[HITLDecision] = Field(..., description="List of decisions for each interrupt")
    user_id: Optional[str] = Field(default=None, description="Firebase user ID")


class AgentResumeResponse(BaseModel):
    """Response from resuming an agent execution"""
    message: str = Field(..., description="Result after resuming")
    thread_id: str = Field(..., description="Thread ID")
    completed: bool = Field(..., description="Whether execution completed or hit another interrupt")
