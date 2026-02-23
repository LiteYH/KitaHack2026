"""Supervisor Agent – coordinates specialized subagents as tools."""

import uuid
from typing import Optional

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphInterrupt
from langgraph.types import Command
from langgraph.types import interrupt as lg_interrupt

from app.core.config import settings
from app.agents.competitor_monitoring import create_competitor_monitoring_agent


def create_supervisor_agent(
    cron_service=None,
    firestore_client=None,
    user_id: Optional[str] = None,
):
    """
    Create the main supervisor agent with subagents as tools.

    Subagents:
    - competitor_monitoring: Research and monitor competitors
    """

    # ── Initialize specialized subagents ─────────────────────────────
    competitor_agent = create_competitor_monitoring_agent(
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
    async def competitor_monitoring(task: str, config: RunnableConfig) -> str:
        """
        Delegate competitor research and monitoring tasks to the specialized Competitor Monitoring Agent.
        
        USE THIS TOOL when the user wants to:
        - Research a specific competitor by name ("Research Nike", "What is Tesla doing?")
        - Find current competitor information (products, pricing, news, strategy)
        - Monitor competitor activities continuously ("Track Adidas daily")
        - Set up scheduled competitor tracking with alerts
        - Get competitive intelligence reports
        - Compare competitor positioning or strategies
        
        DO NOT USE this tool for:
        - General marketing advice (answer directly)
        - Conceptual questions about marketing (answer directly)
        - Questions about your own capabilities (answer directly)
        
        Args:
            task: CLEAR, SPECIFIC description of what the user wants to know about competitors.
                  
                  Good examples:
                  - "Research Nike's recent product launches and pricing strategy in 2026"
                  - "Find news and social media activity for Spotify from the past 2 weeks"
                  - "Set up daily monitoring for Amazon to track their pricing and product changes"
                  - "Compare Apple and Samsung's recent smartphone launches"
                  
                  Bad examples:
                  - "Check competitor" (missing: which competitor? what aspects?)
                  - "Monitor" (missing: who? how often? what to track?)
                  - "Look stuff up" (vague, no specifics)
                  
        Returns:
            Comprehensive analysis, research findings, or monitoring configuration status
            from the Competitor Monitoring specialist.
        """
        import logging
        logger = logging.getLogger(__name__)

        # ── HITL-aware subagent invocation ───────────────────────────────────
        #
        # PROBLEM: monitoring tools use interrupt() inside the SUBAGENT graph.
        # In LangGraph 1.0.x, when ainvoke() encounters an interrupt it RETURNS
        # {"__interrupt__": [...]} instead of raising GraphInterrupt. Without
        # handling this the interrupt is silently swallowed and the frontend
        # never sees a HITL card.
        #
        # SOLUTION:
        #   1. Use a DETERMINISTIC subagent thread derived from the supervisor’s
        #      thread_id so the subagent’s InMemorySaver checkpoint persists
        #      across the interrupt–resume cycle.
        #   2. On the FIRST invocation, if ainvoke returns __interrupt__, re-raise
        #      it at the supervisor level using lg_interrupt() — which PAUSES the
        #      supervisor graph and surfaces the HITL card.
        #   3. On the RESUME invocation, the supervisor re-runs this tool node.
        #      get_state() on the subagent shows it still has a pending task.
        #      We call lg_interrupt() here too — LangGraph detects this is the
        #      same interrupt position in a resumed node and RETURNS the
        #      approval decision instead of raising.
        #   4. We forward that decision to the subagent via Command(resume=...).
        # ──────────────────────────────────────────────────────────────────────

        # Derive a deterministic thread from the supervisor’s thread so the
        # subagent’s checkpoint is reachable on resume.
        supervisor_thread_id = config.get("configurable", {}).get("thread_id") or str(uuid.uuid4())
        subagent_thread = f"hitl_{supervisor_thread_id}"
        subagent_config = {"configurable": {"thread_id": subagent_thread}}
        logger.info(f"[SUPERVISOR→COMPETITOR] supervisor_thread={supervisor_thread_id}, subagent_thread={subagent_thread}, task={task[:200]}")

        try:
            # ―― Check if the subagent has a pending interrupted task ――
            # (means we’re in the RESUME path of a previous HITL flow)
            subagent_interrupted = False
            subagent_interrupt_value = None
            try:
                state = competitor_agent.get_state(subagent_config)
                if state.next:  # graph is paused waiting to continue
                    subagent_interrupted = True
                    # Retrieve the interrupt payload stored by the monitoring tool
                    for pending_task in state.tasks:
                        if hasattr(pending_task, "interrupts") and pending_task.interrupts:
                            subagent_interrupt_value = pending_task.interrupts[0].value
                            break
                    logger.info(f"[SUPERVISOR→COMPETITOR] 🔄 Subagent has pending interrupted state: {state.next}")
            except Exception as state_err:
                logger.debug(f"[SUPERVISOR→COMPETITOR] Could not read subagent state: {state_err}")

            if subagent_interrupted:
                # ―― RESUME PATH ――
                # Surface the stored interrupt value to the supervisor graph.
                # Because the supervisor is currently being RESUMED by the user,
                # LangGraph will detect that lg_interrupt() is being called at the
                # same position as the previous pause and will RETURN the decisions
                # instead of raising again.
                logger.info(f"[SUPERVISOR→COMPETITOR] Surfacing subagent interrupt at supervisor level for resume...")
                decision_value = lg_interrupt(
                    subagent_interrupt_value or {"message": "Awaiting approval to proceed with monitoring changes"}
                )
                logger.info(f"[SUPERVISOR→COMPETITOR] ✅ Decision received: {decision_value}")
                # Forward the decision to the subagent using its saved checkpoint
                result = await competitor_agent.ainvoke(
                    Command(resume=decision_value),
                    config=subagent_config,
                )
            else:
                # ―― FRESH INVOCATION PATH ――
                result = await competitor_agent.ainvoke(
                    {"messages": [{"role": "user", "content": task}]},
                    config=subagent_config,
                )

                # In LangGraph 1.0.x, ainvoke() RETURNS {"__interrupt__": [...]}
                # instead of raising when a tool calls interrupt(). We must
                # detect and re-surface it at the supervisor level.
                if "__interrupt__" in result:
                    interrupts = result["__interrupt__"]
                    interrupt_value = interrupts[0].value if interrupts and hasattr(interrupts[0], "value") else interrupts[0] if interrupts else {}
                    logger.info(f"[SUPERVISOR→COMPETITOR] ⏸️ Subagent interrupted — surfacing HITL at supervisor level")
                    # lg_interrupt() RAISES on the first call (pauses supervisor).
                    # On the resumed call it RETURNS the decision.
                    decision_value = lg_interrupt(interrupt_value)
                    logger.info(f"[SUPERVISOR→COMPETITOR] ✅ Post-interrupt decision: {decision_value}")
                    # Forward to subagent (only reached on resume)
                    result = await competitor_agent.ainvoke(
                        Command(resume=decision_value),
                        config=subagent_config,
                    )

            logger.info(result)

            # Extract the final AI response
            messages = result.get("messages", []) if isinstance(result, dict) else []
            if not messages:
                return "Unable to process competitor monitoring request."

            # Walk backwards to find the last AI message with content
            for msg in reversed(messages):
                if type(msg).__name__ not in ("AIMessage", "AssistantMessage"):
                    continue
                content = getattr(msg, "content", "")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "") if isinstance(b, dict) else str(b)
                        for b in content
                    )
                if content:
                    logger.info(f"[SUPERVISOR→COMPETITOR] ✅ {len(content)} chars")
                    return content

            return "Unable to process competitor monitoring request."

        except GraphInterrupt:
            logger.info("[SUPERVISOR→COMPETITOR] 🔄 GraphInterrupt propagating")
            raise
        except Exception as e:
            logger.error(f"[SUPERVISOR→COMPETITOR] ❌ {e}", exc_info=True)
            return f"Error processing competitor monitoring request: {str(e)}"
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

You are the SUPERVISOR that coordinates specialized agents. Your role is to:
1. **Analyze** the user's request carefully
2. **Decide** if it requires a specialized agent or if you can answer directly
3. **Delegate** to the appropriate specialist with a clear, specific task description
4. **Synthesize** results from specialists and present them clearly to the user

## 🎯 Decision Framework: When to Delegate vs. Answer Directly

### ✅ DELEGATE to specialist agents when the user asks about:
- **Specific competitor research** (names, companies, brands)
- **Real-time competitor data** (current prices, recent launches, news)
- **Monitoring setup** (tracking competitors over time)
- **Competitive intelligence** (market analysis requiring fresh data)
- **Anything requiring web search or external data**

### ✅ ANSWER DIRECTLY when the user asks about:
- **General marketing advice** (strategies, best practices, how-to guides)
- **Conceptual questions** ("What is SEO?" "How does social media work?")
- **Your own capabilities** ("What can you do?" "How do you work?")
- **Clarifying questions** (understanding user needs before delegating)

## 🤖 Available Specialists

### competitor_monitoring
**Use this tool when the user wants to:**
- Research a specific competitor by name (e.g., "Research Nike", "What is Adidas doing?")
- Find recent competitor news, product launches, or pricing changes
- Set up continuous monitoring for a competitor (daily/weekly tracking)
- Check what competitors they're currently monitoring ("What am I monitoring?")
- Modify or delete existing monitoring configurations
- Analyze competitor strategies based on current market data
- Get competitive intelligence reports

**When invoking this tool:**
- Provide a CLEAR, SPECIFIC task description
- Include the competitor name if mentioned
- Specify what aspects to research (products, pricing, news, social, strategy)
- If user wants monitoring management, be specific: "check user competitors", "update Nike monitoring", "delete Adidas monitoring"
- If user wants monitoring setup, explicitly say "set up monitoring for [competitor]"

**Examples:**
```
User: "What is Nike doing lately?"
→ Call tool: "Research Nike's recent activities including product launches, news, and social media updates from the past 30 days"

User: "Monitor Adidas daily"
→ Call tool: "Set up daily monitoring for Adidas to track products, pricing, news, and social media"

User: "What am I monitoring?"
→ Call tool: "Check which competitors the user is currently monitoring and show their status"

User: "Change Nike monitoring to every 2 hours"
→ Call tool: "Update Nike's monitoring frequency to check every 2 hours"

User: "Delete the Adidas monitor"
→ Call tool: "Delete the monitoring configuration for Adidas"

User: "Compare Nike and Adidas pricing"
→ Call tool: "Research and compare current pricing strategies for Nike and Adidas athletic footwear"
```

### General Marketing (You Handle This)
**Answer these directly WITHOUT using tools:**
```
User: "What's a good social media posting frequency?"
→ Answer: "For most SMEs, posting 3-5 times per week on platforms like..."

User: "How do I improve my SEO?"
→ Answer: "Here are key SEO strategies for SMEs: 1. Optimize..."

User: "What can you help me with?"
→ Answer: "I can help you with competitor research, marketing strategy..."
```

## 📋 Response Guidelines

### Formatting:
- Use **Markdown** with bold for emphasis, bullet points for lists
- Use headers (##, ###) to structure longer responses
- Keep responses conversational but professional

### When Delegating to a Specialist:
1. **Invoke the tool immediately** - don't just say you'll do it
2. **Pass a clear, specific task** - include competitor names, timeframes, aspects
3. **After getting results**, present them clearly to the user
4. **Don't add unnecessary commentary** - let the specialist's findings speak

### When Answering Directly:
1. **Be specific and actionable** - give concrete advice, not vague platitudes
2. **Use examples** where relevant
3. **Structure with bullet points** for readability
4. **Suggest follow-ups** if appropriate ("Would you like me to research...?")

## ⚠️ Important Rules

1. **ALWAYS delegate competitor-specific queries** - don't guess or use outdated knowledge
2. **Don't say "I'll" without acting** - if you say you'll research something, invoke the tool immediately
3. **Maintain context** - remember previous messages in the conversation
4. **Be helpful, not robotic** - use a friendly, professional tone
5. **If unsure whether to delegate**, err on the side of delegating

## 🔄 Multi-Step Tasks

For complex requests requiring multiple specialists:
```
User: "Research Adidas, then help me write a marketing strategy"
→ Step 1: Call competitor_monitoring with "Research Adidas's recent strategy..."
→ Step 2: After results, synthesize findings and draft strategy
```

Always complete one specialist task before moving to the next.
"""
    
    # Create supervisor with its own checkpointer for conversation memory
    supervisor = create_agent(
        model=model,
        tools=subagent_tools,
        system_prompt=system_prompt,
        checkpointer=MemorySaver(),
        name="supervisor",
    )
    
    return supervisor
