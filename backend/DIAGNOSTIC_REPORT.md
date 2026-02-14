# Chat UI Streaming Diagnostic Report

**Date:** February 15, 2026  
**Issue:** Agent messages disappearing during intermediate state + HITL not showing

---

## 🔍 Root Cause Analysis

Based on CopilotKit documentation and code review, I've identified the core issue:

### **Problem: Predictive State Not Persisted**

From CopilotKit docs:
> "LangGraph agents are stateful. As a graph is traversed, the state is saved at the end of each node. CopilotKit uses the agent's state as the source of truth for what to display in the frontend chat. However, since state is only emitted at the end of a node, CopilotKit allows you to stream predictive state updates _in the middle of a node_. By default, CopilotKit will stream messages and tool calls being actively generated to the frontend chat that initiated the interaction. **If this predictive state is not persisted at the end of the node, it will disappear in the frontend chat**."

Reference: https://docs.copilotkit.ai/integrations/langgraph/coagent-troubleshooting/common-coagent-issues#i-see-messages-being-streamed-and-disappear

### Current Architecture Issue

```
┌─────────────────────────────────────────────────────────────┐
│ Supervisor Agent                                            │
│  ├─ Invokes competitor_monitoring tool                      │
│  │   └─ Delegates to Competitor Subagent                    │
│  │       ├─ Messages streamed (predictive state) ✓          │
│  │       └─ State saved at end of subagent ✓                │
│  └─ Supervisor extracts only final message                  │
│      └─ Intermediate messages LOST ❌                        │
└─────────────────────────────────────────────────────────────┘
```

**The problem:** In `supervisor.py`, the `competitor_monitoring` tool wrapper only returns the LAST message from the subagent:

```python
@tool
async def competitor_monitoring(task: str, config: RunnableConfig) -> str:
    result = await competitor_agent.ainvoke(...)
    
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]  # ❌ Only returns last message!
        if hasattr(last_message, "content"):
            return last_message.content  # Intermediate messages lost
```

This means:
1. Subagent streams messages (user sees them temporarily)
2. Subagent completes and saves state
3. Supervisor extracts ONLY the final message
4. Supervisor's state doesn't include intermediate messages
5. Frontend shows only what's in supervisor state → messages disappear! 💨

---

## 🛠️ Logging Added

I've added comprehensive logging to trace the entire flow:

### 1. **multi_agent_service.py** - Streaming Layer
- Raw event type debugging
- Token streaming counts
- Interrupt detection and data inspection
- Summary statistics per stream

### 2. **supervisor.py** - Tool Delegation Layer
- Subagent invocation tracking
- Message extraction logging
- Error handling with full context

### 3. **competitor_monitoring/agent.py** - Subagent Layer
- Agent initialization logging
- HITL middleware configuration
- Tool and checkpointer details

### 4. **monitoring_tools.py** - HITL Tool Layer
- Tool invocation tracking
- HITL trigger confirmation
- Config creation and job status
- Service availability checks

---

## 🧪 Testing Instructions

### Step 1: Enable DEBUG Logging (Recommended)

To see detailed event flow, temporarily change log level in `backend/main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
```

### Step 2: Start Backend

```powershell
cd backend
& .venv\Scripts\Activate.ps1
python main.py
```

### Step 3: Start Frontend

```powershell
cd frontend
pnpm run dev
```

### Step 4: Test Scenario 1 - Simple Monitoring Request

In chat:
```
monitor nike
```

Then select:
- Aspects: `news`
- Frequency: `5 minutes once` (or specify frequency)
- Notification: `significant`

**What to observe in logs:**

```
[SUPERVISOR] Starting astream for thread...
[SUPERVISOR→COMPETITOR] Invoking competitor monitoring subagent
[COMPETITOR_AGENT] Creating competitor monitoring agent for user...
[COMPETITOR_AGENT] ✅ HITL middleware configured
[HITL_TOOL] 🔧 create_monitoring_config CALLED
[SUPERVISOR] ⚠️ INTERRUPT DETECTED in thread...
[SUPERVISOR] ✅ Sending X interrupt(s) to frontend
```

### Step 5: Collect Critical Diagnostic Data

Look for these key indicators in logs:

#### ✅ HITL Detection
```
[SUPERVISOR] ⚠️ INTERRUPT #1 DETECTED in thread...
[SUPERVISOR] Number of interrupts: X
[SUPERVISOR] ✅ Sending X interrupt(s) to frontend
```

#### ✅ Message Streaming
```
[SUPERVISOR] Streaming token #1: ...
[SUPERVISOR] Streaming token #2: ...
```

#### ✅ Summary Stats
```
[SUPERVISOR] ✅ Stream completed
[SUPERVISOR] Summary - Messages: X, Tokens: Y, Interrupts: Z
```

---

## 🚨 Expected Findings

Based on the architecture analysis, you should see:

1. **Interrupts ARE being detected** (logs will confirm)
2. **Interrupts ARE being sent to frontend** (JSON payload)
3. **BUT: Frontend may not be displaying them correctly**

The issue is likely:
- **Backend**: Messages from subagent not properly persisted in supervisor state
- **Frontend**: Interrupt handling logic may need review

---

## 💡 Recommended Fixes

### Fix 1: Preserve Intermediate Messages in Supervisor Tool

**Problem:** Supervisor tool only returns final message content.

**Solution Options:**

#### Option A: Return All Messages (Recommended)
Modify `supervisor.py` to return structured data that the supervisor can add to its messages:

```python
@tool
async def competitor_monitoring(task: str, config: RunnableConfig) -> str:
    result = await competitor_agent.ainvoke(...)
    
    # Extract ALL messages, not just the last one
    messages = result.get("messages", [])
    
    # Format as markdown with full context
    response_parts = []
    for msg in messages:
        if hasattr(msg, "content") and msg.content:
            response_parts.append(msg.content)
    
    return "\n\n".join(response_parts)  # Return full conversation
```

#### Option B: Use Command to Update State
Use LangGraph's `Command` to update supervisor state with all messages:

```python
from langgraph.types import Command

@tool
async def competitor_monitoring(task: str, runtime: ToolRuntime) -> Command:
    result = await competitor_agent.ainvoke(...)
    
    # Get all messages from subagent
    subagent_messages = result.get("messages", [])
    
    # Return Command that updates supervisor state
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content="\n\n".join([m.content for m in subagent_messages if hasattr(m, "content")]),
                    tool_call_id=runtime.tool_call_id
                )
            ]
        }
    )
```

### Fix 2: Review Frontend Interrupt Handling

Check `frontend/components/copilotkit/copilot-custom-chat-area.tsx` to ensure:
1. Interrupt events are being received
2. HITL UI components are rendered
3. Resume handlers are wired correctly

### Fix 3: Check CopilotKitMiddleware Configuration

Ensure CopilotKitMiddleware is properly streaming messages in `supervisor.py`:

```python
from copilotkit import CopilotKitMiddleware, copilotkit_customize_config

# In supervisor system prompt or tool handler:
config = copilotkit_customize_config(
    config,
    emit_messages=True,  # Ensure messages are streamed
    emit_tool_calls=True  # Ensure tool calls are streamed
)
```

---

## 📊 Next Steps

1. ✅ **Run the test scenario** with the enhanced logging
2. ✅ **Capture complete logs** from both backend and browser console
3. ✅ **Compare with expected findings** above
4. ✅ **Implement Fix 1** (preserve intermediate messages)
5. ✅ **Test HITL flow** end-to-end
6. ✅ **Verify frontend interrupt rendering**

---

## 📝 Additional Resources

- CopilotKit HITL Docs: https://docs.copilotkit.ai/langgraph/human-in-the-loop
- LangGraph Interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- Subagents Pattern: https://docs.langchain.com/concepts/agents#subagents

---

**Generated by:** GitHub Copilot  
**Status:** Diagnostic logging complete, root cause identified, fixes recommended
