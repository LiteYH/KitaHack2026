"""
Orchestrator Agent.

Simple routing agent that classifies user intent and delegates
to the appropriate specialized agent.  Uses structured output
(response_format) so the LLM returns a clean RoutingDecision.

For Phase 1 only the competitor_monitoring route is wired up.
Other agent routes return a placeholder message.
"""

from typing import Literal, Optional

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from app.core.config import settings


# ── Structured output schema ────────────────────────────────────────

class RoutingDecision(BaseModel):
    """Structured routing decision returned by the orchestrator."""

    agent: Literal[
        "competitor_monitoring",
        "content_planning",
        "competitor_intelligence",
        "publishing",
        "campaign_optimization",
        "roi_dashboard",
        "general_chat",
    ] = Field(description="Which agent should handle this request")
    task: str = Field(description="Brief extracted task description")
    confidence: float = Field(
        description="Confidence in routing decision (0.0 – 1.0)"
    )


# ── Factory ──────────────────────────────────────────────────────────

def create_orchestrator_agent():
    """
    Build a lightweight orchestrator that classifies intent only.

    It has no tools — its sole job is to return a *RoutingDecision*.
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.1,
    )

    system_prompt = """You are the BossolutionAI orchestrator.

Your ONLY job is to classify the user's request and decide which
specialized agent should handle it.  Return a structured routing
decision — do NOT answer the user's question yourself.

## Routing Rules

| Route                    | Trigger examples                                                 |
|--------------------------|------------------------------------------------------------------|
| competitor_monitoring    | "monitor Nike", "track competitor", "set up monitoring",         |
|                          | "what is <company> doing", "research <brand>"                    |
| competitor_intelligence  | "competitive analysis report", "compare us to <company>"        |
| content_planning         | "create content", "plan posts", "content calendar"              |
| publishing               | "publish post", "schedule tweet", "post to Instagram"           |
| campaign_optimization    | "optimize campaign", "improve ads", "A/B test"                  |
| roi_dashboard            | "show ROI", "performance metrics", "analytics dashboard"        |
| general_chat             | greetings, small talk, unclear intent, meta-questions            |

If confidence < 0.7, route to **general_chat** so the user gets a
helpful fallback rather than wrong routing.
"""

    agent = create_agent(
        model=model,
        tools=[],  # no tools — classification only
        system_prompt=system_prompt,
        response_format=RoutingDecision,
        name="orchestrator",
    )

    return agent
