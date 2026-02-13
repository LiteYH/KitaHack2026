# Multi-Agent Subagents Pattern

This system implements the **Subagents Pattern** from LangChain for managing multi-agent conversations.

## Overview

The subagents architecture uses a central supervisor agent that coordinates specialized subagents as tools. This is simpler and more maintainable than the handoffs pattern.

### Key Concept

> "A central main agent (supervisor) coordinates subagents by calling them as tools. The main agent decides which subagent to invoke, what input to provide, and how to combine results."
> — LangChain Documentation

## How It Works

### Architecture

```
User Message
    ↓
Supervisor Agent (maintains context)
    ↓
Decides: Answer directly OR call subagent
    ↓
    ├→ competitor_monitoring tool
    ├→ content_planning tool (TODO)
    ├→ publishing tool (TODO)
    └→ campaign_optimization tool (TODO)
    ↓
Response to User
```

### Example Flow

1. **First Message: "monitor Nike"**
   - User → Supervisor → Decides to call `competitor_monitoring` tool
   - Tool invokes competitor agent with clean context
   - Returns result to supervisor
   - Supervisor responds to user

2. **Follow-up: "what about their social media?"**
   - User → Supervisor (already has full conversation context)
   - Supervisor calls `competitor_monitoring` tool again
   - Tool gets the request AND supervisor maintains the "Nike" context
   - Clean, natural conversation flow

3. **Topic Switch: "give me marketing tips"**
   - User → Supervisor
   - Supervisor answers directly (no subagent needed)
   - Context naturally switches

## Architecture Components

### Supervisor Agent
**Location:** `app/agents/supervisor.py`

The main coordinator that:
- Maintains full conversation history
- Decides when to call subagents vs. answer directly
- Has specialized subagents wrapped as tools
- Provides general marketing assistance

```python
@tool
def competitor_monitoring(task: str) -> str:
    """Research competitors or set up monitoring."""
    result = competitor_agent.invoke({"messages": [{"role": "user", "content": task}]})
    return result["messages"][-1].content
```

### MultiAgentService
**Location:** `app/services/multi_agent_service.py`

Simplified service that just wraps the supervisor:

```python
async def chat_stream(message, thread_id, user_id):
    # Simply stream from supervisor - that's it!
    for mode, chunk in self._supervisor.stream(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode=["messages", "updates"],
    ):
        yield chunk
```

### Specialized Subagents

Each subagent is a standalone agent optimized for its domain:

1. **Competitor Monitoring** (`app/agents/competitor_monitoring/`)
   - Research competitors
   - Analyze activities
   - Set up continuous monitoring
   - Already implemented ✅

2. **Content Planning** (TODO - your teammates)
   - Create content
   - Plan schedules
   - Manage calendars

3. **Publishing** (TODO)
   - Post to social media
   - Schedule posts

4. **Campaign Optimization** (TODO)
   - Analyze campaigns
   - Suggest improvements

5. **ROI Dashboard** (TODO)
   - Show metrics
   - Generate reports

## Adding New Subagents

When your teammates add new agents, follow this pattern:

### 1. Create the Specialized Agent

```python
# app/agents/content_planning/agent.py
def create_content_planning_agent():
    model = ChatGoogleGenerativeAI(...)
    
    tools = [create_post, schedule_post, ...]
    
    system_prompt = """You are the Content Planning Specialist..."""
    
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
        name="content_planning",
    )
```

### 2. Wrap as Tool in Supervisor

```python
# app/agents/supervisor.py

# Initialize the subagent
content_agent = create_content_planning_agent()

# Wrap as tool
@tool
def content_planning(task: str) -> str:
    """
    Create content, plan posts, or manage content calendar.
    
    Use this when the user wants to:
    - Generate social media posts
    - Create content calendars
    - Plan content strategy
    """
    result = content_agent.invoke(
        {"messages": [{"role": "user", "content": task}]}
    )
    
    messages = result.get("messages", [])
    if messages:
        return messages[-1].content
    return "Unable to process content planning request."

# Add to subagent_tools list
subagent_tools = [
    competitor_monitoring,
    content_planning,  # <-- Add here
    # ... others
]
```

### 3. Update Supervisor Prompt

```python
system_prompt = """...

### Content Planning Agent
- Create social media posts
- Plan content calendars
- Develop content strategies

Use the `content_planning` tool for these tasks.

..."""
```

That's it! The supervisor will now intelligently call your agent when needed.

## Benefits of Subagents Pattern

✅ **Simpler** - No state management needed, supervisor handles context
✅ **Context Isolation** - Each subagent gets clean context for its task
✅ **Natural Conversation** - Supervisor maintains full conversation flow
✅ **Flexible** - Supervisor decides when to delegate vs. answer directly
✅ **Maintainable** - Easy to add new agents without complex routing logic
✅ **Scalable** - Add unlimited subagents as team grows

## Comparison with Old Pattern

### Before (Handoffs Pattern - Complex ❌)
```
Message → Check state → Orchestrator (if no state) → Route to agent → Save state
Next message → Check state → Use saved agent → Agent processes
```
- Required Firestore state management
- Complex routing logic
- State expiration handling
- Explicit handoff tools

### Now (Subagents Pattern - Simple ✅)
```
Message → Supervisor (with context) → Decide → Call subagent OR answer
Next message → Supervisor (already has context) → Decide → ...
```
- No state management
- Supervisor decides naturally
- Context flows automatically
- Much simpler!

## Files Structure

```
backend/
├── app/
│   ├── agents/
│   │   ├── supervisor.py              # Main coordinator ⭐
│   │   └── competitor_monitoring/     # Your subagent
│   │       ├── agent.py
│   │       ├── tools/
│   │       └── skills/
│   └── services/
│       └── multi_agent_service.py    # Simplified wrapper ⭐
└── SUBAGENTS_PATTERN.md              # This file
```

## Deprecated Files

The following files are from the old handoffs pattern and can be ignored:

- ❌ `app/core/thread_state.py` - State management (not needed)
- ❌ `app/agents/handoff_tools.py` - Handoff tools (not needed)
- ❌ `app/agents/orchestrator.py` - Old classifier (replaced by supervisor)
- ❌ `app/services/orchestrator_service.py` - Old routing (replaced by supervisor)
- ❌ `app/services/agent_registry.py` - Old registry (not needed)
- ❌ `HANDOFFS_PATTERN.md` - Old documentation

## Debugging

### Check What Supervisor Is Doing

Look for these log messages:

```
[SUPERVISOR] Initialized supervisor agent with subagents
[SUPERVISOR] Processing message in thread abc123
[SUPERVISOR] Streaming message in thread abc123: monitor Nike
```

### Test Supervisor Directly

```python
from app.agents.supervisor import create_supervisor_agent
from app.core.competitor_agent_memory import HybridMemoryManager

supervisor = create_supervisor_agent(HybridMemoryManager())

result = supervisor.invoke(
    {"messages": [{"role": "user", "content": "monitor Nike"}]},
    config={"configurable": {"thread_id": "test-123"}}
)

print(result["messages"][-1].content)
```

## Common Issues

### Issue: Supervisor answers directly instead of calling subagent
**Cause:** Tool description not clear enough
**Solution:** Update tool description in `supervisor.py` to be more specific

### Issue: Subagent doesn't have context
**Cause:** This is expected! Subagents are stateless
**Solution:** Supervisor provides context in the task description

### Issue: Need to access subagent directly
**Cause:** Some admin/cron tasks need direct access
**Solution:** Keep `competitor_agent_service.py` for direct access

## References

- [LangChain Subagents Pattern](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents)
- [Personal Assistant Tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents-personal-assistant)
- Supervisor Agent: `app/agents/supervisor.py`
- Multi-Agent Service: `app/services/multi_agent_service.py`
