"""
Supervisor Agent (Subagents Pattern)

Main coordinator agent that manages specialized subagents as tools.
This replaces the old orchestrator + handoffs pattern with a simpler
subagents architecture.

Based on LangChain's subagents pattern:
"A central main agent (supervisor) coordinates subagents by calling them as tools.
The main agent decides which subagent to invoke, what input to provide, 
and how to combine results."
"""

from typing import Optional

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings
from app.core.competitor_agent_memory import HybridMemoryManager
from app.agents.competitor_monitoring import create_competitor_monitoring_agent


def create_supervisor_agent(
    memory_manager: Optional[HybridMemoryManager] = None,
    cron_service=None,
    firestore_client=None,
    user_id: Optional[str] = None,
):
    """
    Create the main supervisor agent with subagents as tools.
    
    The supervisor:
    - Maintains conversation context across turns
    - Decides which specialized agent to invoke
    - Handles general marketing questions directly
    - Coordinates complex multi-step workflows
    
    Args:
        memory_manager: Optional memory manager for cross-thread memory
        cron_service: CronService instance for monitoring jobs
        firestore_client: Firestore client for saving configurations
        user_id: User ID for the current session
    
    Subagents:
    - competitor_monitoring: Research and monitor competitors
    - content_planning: Content creation and scheduling (TODO)
    - publishing: Social media publishing (TODO)
    - campaign_optimization: Campaign analysis (TODO)
    - roi_dashboard: Analytics and reporting (TODO)
    """
    
    # ── Initialize specialized subagents ─────────────────────────────
    competitor_agent = create_competitor_monitoring_agent(
        memory_manager,
        cron_service=cron_service,
        firestore_client=firestore_client,
        user_id=user_id,
    )
    
    # TODO: Initialize other subagents as your teammates build them
    # content_agent = create_content_planning_agent()
    # publishing_agent = create_publishing_agent()
    # etc.
    
    # ── Wrap subagents as tools ──────────────────────────────────────
    
    @tool
    async def competitor_monitoring(task: str) -> str:
        """
        Research competitors, analyze their activities, or set up continuous monitoring.
        
        Use this when the user wants to:
        - Research a specific competitor
        - Monitor competitor activities (products, pricing, news, social media)
        - Set up scheduled competitor tracking
        - Get competitor intelligence reports
        
        Args:
            task: Clear description of what the user wants to know about competitors
            
        Returns:
            Analysis results or monitoring configuration status
        """
        # Invoke the competitor subagent with a clean context (use ainvoke for async tools)
        result = await competitor_agent.ainvoke(
            {"messages": [{"role": "user", "content": task}]}
        )
        
        # Extract and return only the final response
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content"):
                return last_message.content
        
        return "Unable to process competitor monitoring request."
    
    # TODO: Add more subagent tools as they're built
    # @tool
    # def content_planning(task: str) -> str:
    #     """Create content, plan posts, or manage content calendar."""
    #     ...
    
    # @tool
    # def publishing(task: str) -> str:
    #     """Publish or schedule posts to social media platforms."""
    #     ...
    
    # Collect all subagent tools
    subagent_tools = [
        competitor_monitoring,
        # content_planning,
        # publishing,
        # etc.
    ]
    
    # ── Build supervisor agent ───────────────────────────────────────
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )
    
    system_prompt = """You are BossolutionAI, an AI-powered marketing assistant for SMEs.

You coordinate a team of specialized agents to help with various marketing tasks.
Your job is to:
1. Understand what the user needs
2. Decide which specialized agent can best help
3. Delegate tasks to the appropriate agent
4. Synthesize results and provide clear responses

## Available Specialists

### Competitor Monitoring Agent
- Research competitors and their activities
- Set up continuous monitoring (products, pricing, news, social)
- Analyze competitor strategies
- Track market changes

Use the `competitor_monitoring` tool for these tasks.

### General Marketing Support (You)
For general questions about marketing, strategy, or advice that doesn't require
a specialist, answer directly based on your knowledge.

## Response Guidelines
- Use **Markdown formatting** for readability
- Be conversational and helpful
- When delegating to a specialist, explain why
- If a task needs multiple specialists, coordinate them
- Always maintain context from previous messages
- For competitor-related tasks, use the specialist - don't try to answer yourself

## Examples

User: "Monitor Nike's social media"
→ Use competitor_monitoring tool with clear task description

User: "What's a good social media posting frequency?"
→ Answer directly with marketing best practices

User: "Research Adidas and create content about their strategy"
→ First use competitor_monitoring, then help draft content based on results
"""
    
    # Create supervisor with subagent tools and checkpointer for memory
    checkpointer = (
        memory_manager.checkpointer if memory_manager else InMemorySaver()
    )
    
    supervisor = create_agent(
        model=model,
        tools=subagent_tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        name="supervisor",
    )
    
    return supervisor
