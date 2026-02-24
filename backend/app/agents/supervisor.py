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
from app.services.agents.content_agent import ContentAgent
from app.services.roi_tool import roi_analysis_tool


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
    
    # Content planning agent (stateful, reuses same instance per supervisor)
    content_agent_instance = ContentAgent()
    
    # ── Subagent thread registry ─────────────────────────────────────
    # Maps supervisor_thread_id → active subagent thread_id.
    # A fresh UUID is assigned per user request and stored here.
    # On HITL resume the same thread is reused so the subagent
    # checkpoint is found. Cleared when the subagent completes.
    _active_subagent_threads: dict = {}

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
        # ―― Dynamic thread management ―――――――――――――――――――――――――――――――
        # Each NEW user request gets a fresh UUID so it starts with a clean
        # InMemorySaver checkpoint (no stale ToolMessages from prior turns).
        # During an active HITL cycle the same UUID is reused so the subagent's
        # paused state is found on resume. Cleared when the subagent finishes.
        existing_thread = _active_subagent_threads.get(supervisor_thread_id)
        subagent_interrupted = False
        subagent_interrupt_value = None
        state = None

        if existing_thread:
            try:
                state = competitor_agent.get_state({"configurable": {"thread_id": existing_thread}})
                if state.next:  # graph is paused — we're in a HITL resume cycle
                    subagent_interrupted = True
                    for pending_task in state.tasks:
                        if hasattr(pending_task, "interrupts") and pending_task.interrupts:
                            subagent_interrupt_value = pending_task.interrupts[0].value
                            break
            except Exception as state_err:
                logger.debug(f"[SUPERVISOR] Could not read subagent state: {state_err}")

        if subagent_interrupted:
            subagent_thread = existing_thread
        else:
            subagent_thread = str(uuid.uuid4())
            _active_subagent_threads[supervisor_thread_id] = subagent_thread

        subagent_config = {"configurable": {"thread_id": subagent_thread}}
        logger.info(f"[SUPERVISOR→COMPETITOR] supervisor_thread={supervisor_thread_id}, subagent_thread={subagent_thread}, task={task[:200]}")

        try:

            if subagent_interrupted:
                # -- RESUME PATH --
                # Exactly ONE lg_interrupt() call (pos 0 of this task execution)
                # to receive the user's current decision, then ONE ainvoke() to
                # forward that decision to the subagent.
                #
                # WHY NO LOOP:
                # LangGraph tracks interrupt() calls by call-order position within
                # a task execution.  Each resume turn replays positions 0..N-1 with
                # stored decisions, delivering the NEW decision only to position N.
                # If we call lg_interrupt() twice (pos 0 to get decision1, pos 1 to
                # surface interrupt2), the next resume turn replays pos 0 with
                # decision1 and sends it to interrupt2 -- causing approvals to land
                # on the wrong action or old rejections to persist.
                #
                # FIX: after forwarding the decision and resuming the subagent, if
                # the subagent hits a CHAINED interrupt we return a sentinel string
                # instead of calling lg_interrupt() again.  The supervisor model
                # calls competitor_monitoring once more (brand-new task, fresh pos 0)
                # which surfaces the chained interrupt without any history baggage.
                stored_interrupts = []
                try:
                    for pending_task in state.tasks:
                        if hasattr(pending_task, "interrupts") and pending_task.interrupts:
                            stored_interrupts.extend(pending_task.interrupts)
                except Exception:
                    pass
                if not stored_interrupts:
                    from langgraph.types import Interrupt as LGInterrupt
                    stored_value = subagent_interrupt_value or {
                        "message": "Awaiting approval to proceed with monitoring changes"
                    }
                    stored_interrupts = [LGInterrupt(value=stored_value, resumable=True, ns=[], when="during")]

                first_si       = stored_interrupts[0]
                interrupt_val_r = first_si.value if hasattr(first_si, "value") else first_si
                interrupt_id_r  = getattr(first_si, "id", None)
                logger.info(f"[SUPERVISOR] Resume: surfacing stored interrupt id={interrupt_id_r}")

                # THE sole lg_interrupt() call for this task execution (pos 0).
                decision = lg_interrupt(interrupt_val_r)
                logger.info(f"[SUPERVISOR] Decision received: {decision}")

                resume_payload = {interrupt_id_r: decision} if interrupt_id_r else decision
                result = await competitor_agent.ainvoke(
                    Command(resume=resume_payload),
                    config=subagent_config,
                )

                if result.get("__interrupt__") if isinstance(result, dict) else False:
                    # Chained interrupt: subagent needs another approval.
                    # Do NOT call lg_interrupt() here -- doing so would be pos 1,
                    # and future resume turns would replay this turn's decision at
                    # pos 0 instead of awaiting the user's new input.
                    # Return a sentinel so the supervisor model triggers a new
                    # competitor_monitoring call (fresh task, clean pos 0).
                    chained = result["__interrupt__"][0]
                    cv = chained.value if hasattr(chained, "value") else {}
                    cname = cv.get("competitor", "the competitor") if isinstance(cv, dict) else "the competitor"
                    logger.info("[SUPERVISOR] Chained interrupt detected -- returning AWAITING_NEXT_APPROVAL (no extra lg_interrupt)")
                    # Keep thread in _active_subagent_threads so next call can resume
                    return (
                        f"AWAITING_NEXT_APPROVAL: Another approval is needed for {cname}. "
                        "Call competitor_monitoring again with the exact same original task."
                    )
                # Subagent completed without further interrupts -- fall through.

            else:
                # -- FRESH INVOCATION PATH --
                result = await competitor_agent.ainvoke(
                    {"messages": [{"role": "user", "content": task}]},
                    config=subagent_config,
                )

                if result.get("__interrupt__") if isinstance(result, dict) else False:
                    # Surface the first HITL interrupt.
                    # Exactly ONE lg_interrupt() call per fresh-task execution.
                    # No loop needed -- chained interrupts are handled turn-by-turn
                    # via the RESUME PATH above.
                    first_fi = result["__interrupt__"][0]
                    iv  = first_fi.value if hasattr(first_fi, "value") else first_fi
                    iid = getattr(first_fi, "id", None)
                    logger.info(f"[SUPERVISOR] Fresh path: surfacing HITL id={iid}")
                    lg_interrupt(iv)
                    # lg_interrupt() raises here -- supervisor pauses.
                    # Next HTTP request enters the RESUME PATH above.

            # -- Subagent completed successfully (no pending interrupts) --
            logger.info(result)
            # Subagent completed  release its thread so the next fresh request
            # gets a clean checkpoint (no stale messages from this cycle).
            _active_subagent_threads.pop(supervisor_thread_id, None)

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
    @tool
    async def content_planning(task: str) -> str:
        """
        Delegate content creation and social media planning tasks to the Content Planning Agent.

        USE THIS TOOL when the user wants to:
        - Write or generate social media posts, captions, or content
        - Create marketing copy for any platform (Instagram, Facebook, LinkedIn, TikTok, etc.)
        - Get scheduling recommendations for posts
        - Generate images or visuals for social media
        - Draft content calendars or post ideas
        - Improve or rewrite existing content

        DO NOT USE this tool for:
        - Competitor research (use competitor_monitoring instead)
        - General marketing strategy questions (answer directly)

        Args:
            task: Clear description of the content the user wants to create, including
                  platform, tone, topic, and any other relevant details.

        Returns:
            Generated social media content, scheduling insights, or image generation results.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[SUPERVISOR→CONTENT] task={task[:200]}")
        try:
            result = await content_agent_instance.run(task)
            logger.info(f"[SUPERVISOR→CONTENT] ✅ {len(result)} chars")
            return result
        except Exception as e:
            logger.error(f"[SUPERVISOR→CONTENT] ❌ {e}", exc_info=True)
            return f"Error processing content planning request: {str(e)}"

    # ── Build supervisor agent ───────────────────────────────────────
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )
    
    # Set model for ROI tool so it can generate AI insights
    roi_analysis_tool.set_model(model)

    @tool
    async def roi_analysis(task: str, config: RunnableConfig) -> str:
        """
        Delegate ROI, revenue, video performance, and analytics queries to the ROI Analysis Agent.

        USE THIS TOOL when the user asks about:
        - ROI (Return on Investment) or profit/revenue/earnings/costs
        - Video performance metrics (views, likes, comments, engagement, retention)
        - Analytics or performance data insights
        - Marketing campaign effectiveness
        - Time-based performance queries ("last 7 days", "this month", etc.)
        - Comparing video or content performance over time

        DO NOT USE this tool for:
        - Competitor research (use competitor_monitoring instead)
        - Content creation (use content_planning instead)
        - General marketing advice (answer directly)

        Args:
            task: The user's question about ROI or performance metrics, as stated.

        Returns:
            AI analysis of the user's ROI data with insights and chart data.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[SUPERVISOR→ROI] task={task[:200]}")
        try:
            user_email = config.get("configurable", {}).get("user_email", "")
            result_json = await roi_analysis_tool._arun(
                user_message=task,
                user_email=user_email,
            )
            # Parse JSON result and return the analysis text
            import json as _json
            try:
                data = _json.loads(result_json)
                analysis = data.get("analysis", result_json)
                logger.info(f"[SUPERVISOR→ROI] ✅ {len(str(analysis))} chars")
                return analysis
            except Exception:
                return result_json
        except Exception as e:
            logger.error(f"[SUPERVISOR→ROI] ❌ {e}", exc_info=True)
            return f"Error processing ROI analysis request: {str(e)}"

    subagent_tools = [
        competitor_monitoring,
        content_planning,
        roi_analysis,
    ]
    
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
- **Content creation** (writing posts, captions, marketing copy, generating images)
- **Social media scheduling** (best times to post, content calendars)
- **ROI / revenue / profit / costs / earnings**
- **Video performance metrics** (views, engagement, retention, watch time)
- **Analytics, performance data, or campaign effectiveness**

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

### content_planning
**Use this tool when the user wants to:**
- Write, generate, or draft social media posts, captions, or content
- Create marketing copy for Instagram, Facebook, LinkedIn, TikTok, Twitter, Pinterest, YouTube
- Get AI-generated images or visuals for a post
- Receive scheduling recommendations (best time to post)
- Build a content calendar or brainstorm post ideas

**Examples:**
```
User: "Write an Instagram post about our new coffee blend"
→ Call tool: "Write an engaging Instagram post about a new coffee blend product"

User: "Create a LinkedIn post about our company milestone"
→ Call tool: "Create a professional LinkedIn post celebrating a company milestone"

User: "Generate a Facebook ad for our sale"
→ Call tool: "Generate a Facebook ad post for a product sale with a strong call to action"

User: "Make me a post with an image"
→ Call tool: "Create a social media post with an image for the user's request"
```

## 🖼️ CRITICAL: Image Generation Follow-up Rule

The content_planning agent has an internal **stateful image generation flow**. After generating content it sometimes offers to also create an image. When it does, the conversation is NOT finished — the agent is waiting for confirmation.

**RULE: If the PREVIOUS assistant turn called content_planning AND the result contained the phrase "Image Generation Available" or asked about generating an image, then ANY follow-up message from the user (no matter how short: "yes", "no", "instagram", "facebook", etc.) MUST be forwarded VERBATIM to the content_planning tool. NEVER answer those follow-ups yourself.**

```
Previous content_planning result included "🎨 Image Generation Available!"

User: "yes"
→ DO NOT answer directly. Call tool: "yes"

User: "instagram"
→ DO NOT answer directly. Call tool: "instagram"

User: "yes, instagram"
→ DO NOT answer directly. Call tool: "yes, instagram"

User: "no thanks"
→ DO NOT answer directly. Call tool: "no thanks"
```

**If you answer these follow-ups yourself (e.g. "Great! Which platform?"), the image generation state is broken and the image will NEVER be generated.**

### roi_analysis
**Use this tool when the user asks about:**
- ROI (Return on Investment), revenue, profit, earnings, costs, or budget
- Video performance metrics (views, likes, comments, shares, engagement rate)
- Analytics or data insights for their content
- Marketing campaign effectiveness or performance trends
- Time-based performance queries ("last 7 days", "this month", "last week")
- Comparing performance across videos or time periods

**Examples:**
```
User: "What is my ROI for the last 7 days?"
→ Call tool: "What is my ROI for the last 7 days?"

User: "Show me my best performing videos this month"
→ Call tool: "Show me my best performing videos this month"

User: "How much revenue did I make last month?"
→ Call tool: "How much revenue did I make last month?"

User: "Analyze my video engagement trends"
→ Call tool: "Analyze my video engagement trends"
```

### General Marketing (You Handle This)
**Answer these directly WITHOUT using tools:**
```
User: "What's a good social media posting frequency?"
→ Answer: "For most SMEs, posting 3-5 times per week on platforms like..."

User: "How do I improve my SEO?"
→ Answer: "Here are key SEO strategies for SMEs: 1. Optimize..."

User: "What can you help me with?"
→ Answer: "I can help you with competitor research, content creation, marketing strategy..."
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
6. **NEVER intercept content_planning follow-ups** - if the last tool result contained "Image Generation Available", forward ALL user replies directly to content_planning without modification
7. **ALWAYS delegate ROI/performance/analytics queries** - don't guess numbers, the user's real data is in Firebase

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
