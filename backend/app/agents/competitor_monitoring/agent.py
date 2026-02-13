"""
Competitor Monitoring Agent.

Uses LangChain 1.0 `create_agent` with:
- Google Gemini as the LLM
- Tavily search tools for competitor research
- Agent Skills for domain expertise (progressive disclosure)
- HumanInTheLoopMiddleware for monitoring config approval (Phase 2)
- InMemorySaver for thread-level checkpoints

Phase 1: Basic search + analysis (no HITL, no GenUI).
Phase 2: Add HITL approval flow.
Phase 3: Add cron job execution.
Phase 4: Add GenUI rich responses.
"""

from pathlib import Path
from typing import Optional

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings
from app.core.competitor_agent_memory import HybridMemoryManager

from .skills import SkillLoader, SkillMiddleware
from .tools import (
    create_monitoring_config,
    search_competitor,
    search_competitor_news,
)
from .tools.monitoring_tools import set_monitoring_services

# ── Paths ────────────────────────────────────────────────────────────
SKILLS_DIR = Path(__file__).parent / "skills"


def create_competitor_monitoring_agent(
    memory_manager: Optional[HybridMemoryManager] = None,
    cron_service=None,
    firestore_client=None,
    user_id: Optional[str] = None,
):
    """
    Create the competitor monitoring agent.

    Args:
        memory_manager: Optional memory manager for cross-thread memory
        cron_service: CronService instance for creating monitoring jobs
        firestore_client: Firestore client for saving configurations
        user_id: User ID for the current session

    Returns a compiled LangGraph agent that can be invoked or streamed.
    """
    # Inject services into tools
    set_monitoring_services(cron_service, firestore_client, user_id)
    # ── LLM ──────────────────────────────────────────────────────────
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )

    # ── Skills (progressive disclosure via middleware) ──────────────
    skill_loader = SkillLoader(SKILLS_DIR)
    skill_middleware = SkillMiddleware(
        skill_loader,
        skill_names=["competitor_search", "competitor_analysis", "notification_management"]
    )

    # ── Human-in-the-Loop Middleware (Phase 2) ──────────────────────
    hitl_middleware = HumanInTheLoopMiddleware(
        interrupt_on={
            "create_monitoring_config": {
                "allowed_decisions": ["approve", "edit", "reject"],
                "description": "Monitoring configuration requires approval before activation"
            },
            # Auto-approve search tools
            "search_competitor": False,
            "search_competitor_news": False,
        },
        description_prefix="Monitoring setup pending approval",
    )

    # ── Tools ────────────────────────────────────────────────────────
    tools = [
        search_competitor,
        search_competitor_news,
        create_monitoring_config,
    ]

    # ── System prompt ────────────────────────────────────────────────
    system_prompt = f"""You are the **Competitor Monitoring Specialist** of BossolutionAI, \
an AI-powered marketing assistant for SMEs.

Your capabilities:
1. **One-time competitor research** — Search and analyze competitor activities, \
products, pricing, news, and social media using the search tools.
2. **Continuous monitoring setup** — Help users set up scheduled monitoring jobs \
that automatically track competitors at a specified frequency.

When a user asks you to research a competitor:
- Use the `search_competitor` tool with relevant aspects
- Use `search_competitor_news` for recent news
- Summarize findings clearly with bullet points
- Highlight significant developments
- Suggest next steps or monitoring setup if appropriate

When a user asks to set up monitoring:
- Ask what competitor to monitor (if not specified)
- Ask what aspects to track (products, pricing, news, social)
- Suggest an appropriate frequency (default: daily = 24 hours)
- Ask about notification preferences (default: significant_only)
- Use `create_monitoring_config` to create the configuration
- This will trigger an approval request to the user

## IMPORTANT: Post-Approval Messaging
When the user APPROVES the monitoring configuration (you'll receive the tool result):
- DO NOT say "pending approval" - they just approved it!
- Confirm the job is now ACTIVE and running
- Mention the job ID if available in the tool result
- Be specific: "Your monitoring configuration has been approved and is now active!"
- Example: "✅ **Monitoring activated!** I'm now tracking Nike's news daily. Job ID: monitor_abc123. \
You'll receive notifications only for significant updates."

## Response Guidelines
- Use **Markdown formatting** for readability
- Use bullet points and numbered lists
- Bold important findings
- Keep responses concise but thorough
- Always cite sources when available
- If no relevant information is found, say so clearly
- After approval, confirm activation with job details
"""

    # ── Checkpointer (thread-level persistence) ──────────────────────
    checkpointer = (
        memory_manager.checkpointer if memory_manager else InMemorySaver()
    )

    # ── Build agent ──────────────────────────────────────────────────
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[skill_middleware, hitl_middleware],
        checkpointer=checkpointer,
        name="competitor_monitoring",
    )

    return agent
