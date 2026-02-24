# LangGraph HITL Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `langgraph>=0.2.0` - LangGraph agent framework
- `langgraph-checkpoint>=2.0.0` - State checkpointing
- `langchain>=1.2.10` - LangChain core
- All other required packages

## Usage

### 1. Start the Server

```bash
uvicorn main:app --reload
```

### 2. Test with cURL

**Initial ROI Query (triggers approval):**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my ROI for the last 7 days?",
    "user_email": "user@example.com"
  }'
```

**Expected Response:**
```json
{
  "message": "🔒 **Data Access Request**\n\nI need your permission...",
  "requires_approval": true,
  "approval_request": {
    "tool_name": "roi_analysis",
    "thread_id": "abc-123-def",
    ...
  },
  "thread_id": "abc-123-def"
}
```

**Approve the Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "yes",
    "user_email": "user@example.com",
    "thread_id": "abc-123-def",
    "approval_decision": {
      "thread_id": "abc-123-def",
      "approved": true,
      "tool_name": "roi_analysis"
    }
  }'
```

**Expected Response:**
```json
{
  "message": "📊 **Your ROI Analysis**\n\n✅ Overall Performance...",
  "charts": [
    {"type": "bar", "title": "Revenue vs Cost", ...}
  ],
  "requires_approval": false,
  "thread_id": "abc-123-def"
}
```

### 3. Test with Python

```python
import requests

# Step 1: Initial query
response1 = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    json={
        "message": "Show me my ROI for last month",
        "user_email": "user@example.com"
    }
)
data1 = response1.json()

# Check if approval is required
if data1["requires_approval"]:
    thread_id = data1["thread_id"]
    
    # Step 2: User approves
    response2 = requests.post(
        "http://localhost:8000/api/v1/chat/message",
        json={
            "message": "yes",
            "user_email": "user@example.com",
            "thread_id": thread_id,
            "approval_decision": {
                "thread_id": thread_id,
                "approved": True
            }
        }
    )
    data2 = response2.json()
    
    # Display results
    print(data2["message"])
    if data2["charts"]:
        print(f"Charts: {len(data2['charts'])} visualizations")
```

## Key Differences from Previous Implementation

### Before (Custom HITL):
```python
# Custom confirmation tracking
confirmation_request = roi_service.create_confirmation_request(...)
# Manual state management
_pending_confirmations[action_id] = {...}
```

### After (LangGraph HITL):
```python
# Automatic interrupt before tool execution
self.agent = create_react_agent(
    ...,
    interrupt_before=["tools"]  # 🔒 Automatic HITL
)
```

**Benefits:**
- ✅ No manual state management
- ✅ Automatic approval requests
- ✅ Built-in checkpointing
- ✅ Official LangChain pattern

## Frontend Integration Example (React/Next.js)

```typescript
// hooks/useChatWithApproval.ts
import { useState } from 'react';

interface ApprovalRequest {
  tool_name: string;
  thread_id: string;
  message: string;
}

export function useChatWithApproval() {
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequest | null>(null);
  
  const sendMessage = async (message: string, userEmail: string) => {
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_email: userEmail })
    });
    
    const data = await response.json();
    
    if (data.requires_approval) {
      // Show approval dialog
      setPendingApproval({
        tool_name: data.approval_request.tool_name,
        thread_id: data.thread_id,
        message: data.message
      });
      return null;
    }
    
    return data;
  };
  
  const handleApproval = async (approved: boolean, userEmail: string) => {
    if (!pendingApproval) return;
    
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: approved ? 'yes' : 'no',
        user_email: userEmail,
        thread_id: pendingApproval.thread_id,
        approval_decision: {
          thread_id: pendingApproval.thread_id,
          approved,
          tool_name: pendingApproval.tool_name
        }
      })
    });
    
    const data = await response.json();
    setPendingApproval(null);
    return data;
  };
  
  return { sendMessage, handleApproval, pendingApproval };
}
```

```typescript
// components/ChatWithApproval.tsx
import { useChatWithApproval } from '@/hooks/useChatWithApproval';

export default function ChatWithApproval({ userEmail }: { userEmail: string }) {
  const { sendMessage, handleApproval, pendingApproval } = useChatWithApproval();
  
  return (
    <div>
      {pendingApproval && (
        <ApprovalDialog
          message={pendingApproval.message}
          onApprove={() => handleApproval(true, userEmail)}
          onDeny={() => handleApproval(false, userEmail)}
        />
      )}
      
      <ChatInterface
        onSendMessage={(msg) => sendMessage(msg, userEmail)}
      />
    </div>
  );
}
```

## Environment Setup

Ensure your `.env` file has:

```env
# Google AI API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Firebase credentials
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# Or Firebase config
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=your-client-email@...
FIREBASE_PRIVATE_KEY=your-private-key
```

## Troubleshooting

### Issue: "langgraph not found"
**Solution:**
```bash
pip install langgraph langgraph-checkpoint
```

### Issue: "Agent state not found"
**Cause:** Thread ID mismatch or expired state
**Solution:** Ensure the same `thread_id` is used in approval request

### Issue: "Tool executed without approval"
**Cause:** `interrupt_before` not configured correctly
**Solution:** Verify agent setup:
```python
self.agent = create_react_agent(
    ...,
    interrupt_before=["tools"]  # Must be "tools", not ["tool"] or "tool"
)
```

### Issue: State lost after server restart
**Cause:** Using `MemorySaver()` (in-memory)
**Solution:** For production, use `AsyncPostgresSaver`:
```python
from langgraph.checkpoint.postgres import AsyncPostgresSaver

checkpointer = AsyncPostgresSaver(
    conn_string="postgresql://..."
)
```

## Monitoring

Check logs for HITL events:

```
🎯 [AGENT] Processing message with thread_id: abc-123
   ↳ User email: user@example.com
   ↳ Message: What is my ROI?
⏸️ [HITL] Agent interrupted - tool execution requires approval
🔒 [HITL] Tool execution requires approval:
   ↳ Tool: roi_analysis
   ↳ Args: {...}
🔐 [HITL] Processing approval decision: True
✅ [HITL] User approved - resuming agent execution
🎯 [ROI TOOL] Executing ROI analysis for: user@example.com
   ↳ Query: What is my ROI?
   ↳ Note: User already approved via LangGraph HITL
```

## Next Steps

1. **Install dependencies** (`pip install -r requirements.txt`)
2. **Test locally** with cURL or Python
3. **Update frontend** to handle approval flow
4. **Deploy with persistent checkpointer** for production
5. **Add monitoring** and audit logging

## Support

For issues or questions:
- Check `LANGGRAPH_HITL_IMPLEMENTATION.md` for detailed documentation
- Refer to LangChain docs: https://python.langchain.com/docs/langgraph
- Review LangGraph HITL examples: https://langchain-ai.github.io/langgraph/
