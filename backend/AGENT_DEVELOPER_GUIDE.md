# Agent Architecture - Developer Guide

⚠️ **UPDATED FOR SUBAGENTS PATTERN** - See [SUBAGENTS_PATTERN.md](./SUBAGENTS_PATTERN.md) for complete details

## Overview

The multi-agent system uses the **Subagents Pattern** where a central supervisor agent coordinates specialized subagents as tools. Multiple developers can work on different agents simultaneously without conflicts.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (chat.py)                       │
│                                                              │
│  POST /chat/message      - Single turn chat                 │
│  POST /chat/stream       - Streaming chat                   │
│  POST /chat/resume       - Resume interrupted agent (HITL)  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              MultiAgentService                               │
│              (multi_agent_service.py)                        │
│                                                              │
│  - Wraps the supervisor agent                               │
│  - Main entry point for API layer                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Supervisor Agent                                  │
│            (supervisor.py)                                   │
│                                                              │
│  - Maintains conversation context                           │
│  - Calls subagents as tools                                 │
│  - Handles general questions directly                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────────────────────────┐
          ▼                                ▼
┌──────────────────────┐         ┌──────────────────────┐
│ competitor_monitoring│         │ content_planning     │
│      (tool)          │         │     (tool - TODO)    │
│                      │         │                      │
│ Wraps competitor     │         │ Wraps content agent  │
│ agent as a tool      │         │ as a tool            │
└──────────────────────┘         └──────────────────────┘

          ▼                                ▼
┌──────────────────────┐         ┌──────────────────────┐
│ CompetitorAgent      │         │ ContentAgent         │
│                      │         │                      │
│ - Research           │         │ - Create content     │
│ - Monitoring setup   │         │ - Schedule posts     │
└──────────────────────┘         └──────────────────────┘
```

## File Structure

```
backend/app/
├── services/
│   ├── multi_agent_service.py          # Main entry point (DON'T MODIFY)
│   ├── competitor_agent_service.py     # Example: Competitor monitoring
│   └── your_agent_service.py           # YOUR NEW AGENT SERVICE
│
├── agents/
│   ├── supervisor.py                   # Main supervisor (REGISTER YOUR AGENT HERE)
│   ├── competitor_monitoring/
│   │   ├── agent.py                    # Competitor agent
│   │   ├── tools/                      # Agent tools
│   │   └── skills/                     # Agent skills
│   └── your_agent/                     # YOUR NEW AGENT
│       ├── agent.py                    # Your agent definition
│       ├── tools/                      # Your tools
│       └── skills/                     # Your skills (optional)
│
├── core/
│   ├── competitor_agent_memory.py      # Memory management (reusable)
│   └── ...
│
└── api/v1/routers/
    └── chat.py                         # API endpoints (DON'T MODIFY)
```

## How to Add a New Agent

⚠️ **Read [SUBAGENTS_PATTERN.md](./SUBAGENTS_PATTERN.md) first for complete pattern details**

### Step 1: Create Your Agent Service

**Purpose**: The service wraps your agent's invocation logic. This makes it reusable from both the supervisor (as a tool) and from cron jobs (direct access).

Create `app/services/your_agent_service.py`:

```python
"""
Your Agent Service

Describe what your agent does here.
"""

import json
from typing import AsyncGenerator, Optional, List, Dict, Any

from langchain_core.messages import AIMessage
from langgraph.types import Command

from app.agents.your_agent import create_your_agent
from app.core.firebase import get_db
from app.core.competitor_agent_memory import HybridMemoryManager


class YourAgentService:
    """Service for your specialized agent."""

    def __init__(self):
        self._memory_manager: Optional[HybridMemoryManager] = None
        self._agent = None

    def _ensure_init(self):
        """Lazy initialization."""
        if self._agent is not None:
            return

        db = get_db()
        self._memory_manager = HybridMemoryManager(firestore_client=db)
        self._agent = create_your_agent(
            memory_manager=self._memory_manager,
        )

    async def invoke(
        self,
        message: str,
        thread_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """Single-turn invoke (non-streaming)."""
        self._ensure_init()

        result = self._agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def stream(
        self,
        message: str,
        thread_id: str,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream agent responses."""
        self._ensure_init()

        config = {"configurable": {"thread_id": thread_id}}

        for mode, chunk in self._agent.stream(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                token, metadata = chunk
                if isinstance(token, AIMessage) and token.content:
                    yield json.dumps({"type": "token", "content": token.content})

            elif mode == "updates":
                # Handle HITL interrupts if needed
                if "__interrupt__" in chunk:
                    interrupts = chunk["__interrupt__"]
                    interrupt_data = []
                    for interrupt in interrupts:
                        if hasattr(interrupt, 'value'):
                            interrupt_data.append({
                                'id': interrupt.id if hasattr(interrupt, 'id') else None,
                                'value': interrupt.value
                            })
                        else:
                            interrupt_data.append(interrupt)
                    
                    yield json.dumps({
                        "type": "interrupt",
                        "data": interrupt_data,
                    })

    async def resume(
        self,
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> str:
        """Resume interrupted execution (if your agent uses HITL)."""
        self._ensure_init()

        resume_payload = {"decisions": decisions}

        result = self._agent.invoke(
            Command(resume=resume_payload),
            config={"configurable": {"thread_id": thread_id}},
        )

        return self._extract_text(result)

    async def resume_stream(
        self,
        thread_id: str,
        decisions: List[Dict[str, Any]],
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Resume with streaming (if your agent uses HITL)."""
        self._ensure_init()

        resume_payload = {"decisions": decisions}
        config = {"configurable": {"thread_id": thread_id}}

        for mode, chunk in self._agent.stream(
            Command(resume=resume_payload),
            config=config,
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                token, metadata = chunk
                if isinstance(token, AIMessage) and token.content:
                    yield json.dumps({"type": "token", "content": token.content})

            elif mode == "updates":
                if "__interrupt__" in chunk:
                    interrupts = chunk["__interrupt__"]
                    interrupt_data = []
                    for interrupt in interrupts:
                        if hasattr(interrupt, 'value'):
                            interrupt_data.append({
                                'id': interrupt.id if hasattr(interrupt, 'id') else None,
                                'value': interrupt.value
                            })
                        else:
                            interrupt_data.append(interrupt)
                    
                    yield json.dumps({
                        "type": "interrupt",
                        "data": interrupt_data,
                    })

    @staticmethod
    def _extract_text(result: dict) -> str:
        """Extract text from agent result."""
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content
        return "I wasn't able to generate a response. Please try again."


# Singleton instance
your_agent_service = YourAgentService()
```

### Step 2: Wrap Your Agent as a Tool

Edit `app/agents/supervisor.py` to register your agent:

```python
from app.services.competitor_agent_service import competitor_agent_service
from app.services.your_agent_service import your_agent_service  # ADD THIS
from langchain_core.tools import tool

# Existing tool
@tool
async def competitor_monitoring(task: str) -> str:
    """Monitor competitors and their marketing strategies."""
    # ...existing code...

# ADD YOUR TOOL
@tool
async def your_agent_name(task: str) -> str:
    """
    Description of what your agent does. This description helps the supervisor
    decide when to call your agent.
    
    Examples: "Plan content strategy", "Create social media posts", etc.
    """
    thread_id = "internal-your-agent"  # Use a unique internal thread
    result = await your_agent_service.invoke(
        message=task,
        thread_id=thread_id,
    )
    return result

# Update supervisor creation
def create_supervisor_agent():
    tools = [
        competitor_monitoring,
        your_agent_name,  # ADD THIS
    ]
    # ...rest of supervisor setup...
```

### Step 3: Test Your Integration

No need to update the orchestrator or registry - the supervisor will automatically discover your tool!

### Step 4: Create Your Agent

Create `app/agents/your_agent/agent.py`:

```python
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

def create_your_agent(memory_manager=None):
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )
    
    tools = [
        # Your tools here
    ]
    
    system_prompt = """Your agent's system prompt here"""
    
    checkpointer = (
        memory_manager.checkpointer if memory_manager else InMemorySaver()
    )
    
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        name="your_agent_name",
    )
    
    return agent
```

### Step 5: Test Your Agent

```bash
# Start the backend
uvicorn app.main:app --reload

# Test via API (supervisor will route to your agent automatically)
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "your test message", "thread_id": "test-123"}'
```

## Benefits of This Architecture

1. **No Conflicts**: Each agent has its own service file
2. **Easy Testing**: Test your agent independently via supervisor or direct service call
3. **Clean Separation**: Supervisor handles routing, agents focus on their domain
4. **Scalable**: Add as many agents as needed - just wrap as tools
5. **Type Safe**: Full type hints throughout
6. **Context Preservation**: Supervisor maintains conversation flow naturally
7. **HITL Support**: Built-in human-in-the-loop if needed
8. **Direct Access**: Services can be called directly from cron jobs or other services

## Common Patterns

### Agent Without HITL

If your agent doesn't need approval workflows, you can skip the `resume` and `resume_stream` methods.

### Agent With Custom Tools

Create tools in `app/agents/your_agent/tools/`:

```python
from langchain.tools import tool

@tool
def your_tool(param: str) -> str:
    """Tool description."""
    # Your logic here
    return result
```

### Agent With Skills

Use the skills system for progressive disclosure (see `competitor_monitoring/skills/` for examples).

## Need Help?

- Check `competitor_agent_service.py` for a complete example
- Review the Phase 2 implementation docs
- Ask your team lead for guidance

## Common Issues

**Q: My agent isn't being routed to**
A: Make sure it's registered in `agent_registry.py` and the orchestrator knows about it

**Q: HITL isn't working**
A: Ensure your agent uses `HumanInTheLoopMiddleware` and you have a checkpointer

**Q: Imports failing**
A: Make sure you're in the virtual environment: `.venv\Scripts\Activate.ps1`

**Q: Changes not taking effect**
A: Restart uvicorn - it may not hot-reload all files
