"""
Supervisor Agent (Subagents Pattern)

Main coordinator agent that manages specialized subagents as tools.
Uses direct LangGraph streaming (no CopilotKit dependency).
"""

from typing import Optional

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphInterrupt
from langchain_core.runnables import RunnableConfig

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
        
        logger.info(f"[SUPERVISOR→COMPETITOR] Invoking competitor monitoring subagent")
        logger.info(f"[SUPERVISOR→COMPETITOR] Task: {task[:200]}")
        logger.info(f"[SUPERVISOR→COMPETITOR] Config: {config}")
        
        # Invoke the competitor subagent with a clean context
        try:
            result = await competitor_agent.ainvoke(
                {"messages": [{"role": "user", "content": task}]},
                config=config,
            )
            
            logger.info(f"[SUPERVISOR→COMPETITOR] ✅ Subagent completed")
            logger.debug(f"[SUPERVISOR→COMPETITOR] Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
            
            # Extract ALL assistant messages, not just the last one
            # This preserves intermediate conversation states
            messages = result.get("messages", [])
            logger.info(f"[SUPERVISOR→COMPETITOR] Received {len(messages)} messages from subagent")
            
            if not messages:
                logger.warning(f"[SUPERVISOR→COMPETITOR] No messages found in result")
                return "Unable to process competitor monitoring request."
            
            # Collect all AI/assistant message content
            assistant_messages = []
            for i, msg in enumerate(messages):
                msg_type = type(msg).__name__
                has_content = hasattr(msg, "content")
                content_type = type(msg.content).__name__ if has_content else "N/A"
                logger.info(f"[SUPERVISOR→COMPETITOR] Message {i+1}/{len(messages)}: type={msg_type}, has_content={has_content}, content_type={content_type}")
                
                # Log message role if available
                if hasattr(msg, "role"):
                    logger.debug(f"[SUPERVISOR→COMPETITOR] Message {i+1} role: {msg.role}")
                
                # Only include assistant/AI messages (skip user messages, tool calls, etc.)
                if msg_type in ["AIMessage", "AssistantMessage"]:
                    if hasattr(msg, "content") and msg.content:
                        content = msg.content
                        # Handle both string and structured content
                        if isinstance(content, str):
                            content_preview = content[:100] if len(content) > 100 else content
                            logger.info(f"[SUPERVISOR→COMPETITOR] ✓ Adding string message {i+1}: length={len(content)}, preview={content_preview}...")
                            assistant_messages.append(content)
                        elif isinstance(content, list):
                            # Handle structured content (e.g., text blocks)
                            logger.info(f"[SUPERVISOR→COMPETITOR] Processing structured content with {len(content)} blocks")
                            text_content = " ".join([
                                block.get("text", "") if isinstance(block, dict) else str(block)
                                for block in content
                            ])
                            if text_content.strip():
                                logger.info(f"[SUPERVISOR→COMPETITOR] ✓ Adding structured message {i+1}: length={len(text_content)}")
                                assistant_messages.append(text_content)
                            else:
                                logger.warning(f"[SUPERVISOR→COMPETITOR] ✗ Structured content {i+1} is empty after processing")
                        else:
                            logger.warning(f"[SUPERVISOR→COMPETITOR] ✗ Unexpected content type for message {i+1}: {type(content)}")
                    else:
                        logger.warning(f"[SUPERVISOR→COMPETITOR] ✗ Message {i+1} is AIMessage but has no content")
                else:
                    logger.debug(f"[SUPERVISOR→COMPETITOR] ✗ Skipping message {i+1} (not assistant/AI): {msg_type}")
            
            if assistant_messages:
                # Join all messages with paragraph breaks
                # This preserves the full conversation flow
                full_response = "\n\n".join(assistant_messages)
                logger.info(f"[SUPERVISOR→COMPETITOR] ✅ Returning {len(assistant_messages)} message(s)")
                logger.info(f"[SUPERVISOR→COMPETITOR] Total content length: {len(full_response)} chars")
                logger.info(f"[SUPERVISOR→COMPETITOR] Full response preview (first 200 chars): {full_response[:200]}")
                logger.info(f"[SUPERVISOR→COMPETITOR] Full response end (last 100 chars): {full_response[-100:] if len(full_response) > 100 else full_response}")
                return full_response
            
            # Fallback to last message if no assistant messages found
            last_message = messages[-1]
            if hasattr(last_message, "content"):
                content = last_message.content
                logger.info(f"[SUPERVISOR→COMPETITOR] Fallback: returning last message")
                return content if isinstance(content, str) else str(content)
            
            logger.warning(f"[SUPERVISOR→COMPETITOR] No valid messages found in result")
            return "Unable to process competitor monitoring request."
        
        except GraphInterrupt:
            # Don't catch GraphInterrupt - let it propagate to LangGraph's tool executor
            # LangGraph will convert it to an __interrupt__ event in the stream
            logger.info(f"[SUPERVISOR→COMPETITOR] 🔄 GraphInterrupt - propagating to LangGraph")
            raise
        
        except Exception as e:
            # Catch other exceptions
            logger.error(f"[SUPERVISOR→COMPETITOR] ❌ Error invoking subagent: {e}", exc_info=True)
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
- Analyze competitor strategies based on current market data
- Get competitive intelligence reports

**When invoking this tool:**
- Provide a CLEAR, SPECIFIC task description
- Include the competitor name if mentioned
- Specify what aspects to research (products, pricing, news, social, strategy)
- If user wants monitoring, explicitly say "set up monitoring for [competitor]"

**Examples:**
```
User: "What is Nike doing lately?"
→ Call tool: "Research Nike's recent activities including product launches, news, and social media updates from the past 30 days"

User: "Monitor Adidas daily"
→ Call tool: "Set up daily monitoring for Adidas to track products, pricing, news, and social media"

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
    
    # Create supervisor with subagent tools and checkpointer for memory
    checkpointer = (
        memory_manager.checkpointer if memory_manager else MemorySaver()
    )
    
    supervisor = create_agent(
        model=model,
        tools=subagent_tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        name="supervisor",
    )
    
    return supervisor
