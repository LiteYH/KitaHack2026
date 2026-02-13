# Backend Structure Overview

⚠️ **UPDATED FOR MULTI-AGENT ARCHITECTURE** - See [SUBAGENTS_PATTERN.md](./SUBAGENTS_PATTERN.md) for complete pattern details

## 📂 Complete Folder Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/                          # API Layer
│   │   ├── __init__.py
│   │   └── v1/                       # API Version 1
│   │       ├── __init__.py
│   │       └── routers/              # HTTP Endpoints
│   │           ├── __init__.py
│   │           ├── chat.py           ✅ Multi-agent chat endpoint
│   │           ├── monitoring.py     ✅ Competitor monitoring endpoints
│   │           └── items.py          ✅ Basic CRUD endpoints
│   │
│   ├── agents/                       # Agent Definitions
│   │   ├── __init__.py
│   │   ├── supervisor.py             ✅ Main supervisor agent (Subagents pattern)
│   │   └── competitor_monitoring/    ✅ Competitor monitoring agent
│   │       ├── agent.py
│   │       ├── tools/
│   │       └── skills/
│   │
│   ├── core/                         # Core Configuration
│   │   ├── __init__.py
│   │   ├── config.py                 ✅ Firebase, AI keys, environment config
│   │   ├── firebase.py               ✅ Firestore client
│   │   ├── auth.py                   ✅ Firebase authentication
│   │   └── competitor_agent_memory.py ✅ Memory management (reusable)
│   │
│   ├── schemas/                      # Pydantic Models
│   │   ├── __init__.py
│   │   ├── chat.py                   ✅ Chat request/response models
│   │   └── item.py                   ✅ Basic item models
│   │
│   └── services/                     # Business Logic
│       ├── __init__.py
│       ├── multi_agent_service.py    ✅ Main multi-agent coordinator
│       ├── competitor_agent_service.py ✅ Competitor monitoring service
│       ├── monitoring_service.py     ✅ Monitoring operations
│       ├── monitoring_db_service.py  ✅ Monitoring database
│       ├── cron_service.py           ✅ Scheduled tasks
│       ├── notification_service.py   ✅ Notifications
│       └── chat_service.py           ✅ Single-agent chat service
│
├── data/                             # Data Storage
│   └── monitoring.db                 ✅ SQLite for monitoring data
│
├── main.py                           ✅ FastAPI app entry point
├── requirements.txt                  ✅ Python dependencies
├── pyproject.toml                    ✅ Project configuration
├── .env                              ✅ Environment variables
├── .gitignore                        ✅ Git ignore rules
├── README.md                         ✅ Project documentation
├── AGENT_DEVELOPER_GUIDE.md          ✅ Guide for adding new agents
├── SUBAGENTS_PATTERN.md              ✅ Multi-agent pattern documentation
└── MIGRATION_SUMMARY.md              ✅ Migration history
```

## 🔄 Request Flow (Multi-Agent Chat)

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│                  http://localhost:3000                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ POST /api/v1/chat/message
                      │ {"message": "monitor Nike", "thread_id": "chat-123"}
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│                  http://localhost:8000                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              main.py (Entry Point)                   │  │
│  │  • CORS Middleware                                   │  │
│  │  • Router Registration                               │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│                      ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         app/api/v1/routers/chat.py                   │  │
│  │  • POST /chat/message      - Single turn            │  │
│  │  • POST /chat/stream       - Streaming              │  │
│  │  • POST /chat/resume       - Resume after HITL       │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│                      ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    app/services/multi_agent_service.py               │  │
│  │  • Wraps supervisor agent                           │  │
│  │  • Delegates to supervisor for all operations       │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│                      ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         app/agents/supervisor.py                     │  │
│  │  • Main supervisor agent (Subagents pattern)        │  │
│  │  • Maintains conversation context                   │  │
│  │  • Calls subagents as tools                         │  │
│  │  • Handles general questions directly               │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│           ┌──────────┴──────────┐                          │
│           ↓                     ↓                           │
│  ┌─────────────────┐   ┌─────────────────┐                │
│  │ competitor_     │   │ content_        │ (TODO)         │
│  │ monitoring      │   │ planning        │                │
│  │ (tool)          │   │ (tool)          │                │
│  └────────┬────────┘   └─────────────────┘                │
│           │                                                 │
│           ↓                                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app/services/competitor_agent_service.py            │  │
│  │  • Wraps competitor agent invocation                │  │
│  │  • Can be called from supervisor OR directly        │  │
│  │  • Used by cron jobs for scheduled monitoring       │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│                      ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  app/agents/competitor_monitoring/agent.py           │  │
│  │  • Specialized competitor monitoring agent          │  │
│  │  • Tools: research, monitoring setup                │  │
│  │  • Skills: analysis, reporting                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  • Firebase Firestore (user configs, monitoring data)      │
│  • Firebase Authentication (user sessions)                  │
│  • SQLite (monitoring.db - competitor data cache)          │
│  • In-memory checkpointer (conversation state)             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ What You Have Now

### 1. **Multi-Agent Architecture** ✓
- Supervisor agent coordinates all interactions (Subagents pattern)
- Competitor monitoring agent fully functional
- Easy to add new agents - just wrap as tools
- Natural conversation flow with context preservation

### 2. **Chat API** ✓
- Full conversation support with thread management
- Streaming responses
- Human-in-the-loop (HITL) support for approvals
- Resume interrupted workflows

### 3. **Competitor Monitoring** ✓
- Research competitors
- Setup monitoring configurations
- Track marketing strategies
- Scheduled cron jobs for automated monitoring
- Firestore persistence for configs

### 4. **Infrastructure** ✓
- Firebase Firestore for data persistence
- Firebase Authentication for user management
- SQLite for monitoring data cache
- In-memory checkpointers for conversation state
- CORS configured for frontend integration

## 🚀 How to Use Right Now

### 1. Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

Server runs on: **http://localhost:8000**

### 2. View API Documentation

Open in browser: **http://localhost:8000/docs**

### 3. Test Multi-Agent Chat

```typescript
// In your Next.js app
const response = await fetch('http://localhost:8000/api/v1/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'monitor Nike',
    thread_id: 'chat-123'
  })
});
const result = await response.json();
console.log(result.response); // Agent response
```

### 4. Test Streaming Chat

```typescript
const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'analyze Nike marketing strategy',
    thread_id: 'chat-123'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const events = chunk.split('\n\n');
  
  for (const event of events) {
    if (event.startsWith('data: ')) {
      const data = JSON.parse(event.slice(6));
      if (data.type === 'token') {
        console.log(data.content); // Stream tokens
      }
    }
  }
}
```

## 📝 Next Steps

### Option A: Add More Agents (Recommended)

Follow [AGENT_DEVELOPER_GUIDE.md](./AGENT_DEVELOPER_GUIDE.md) to add new agents:
1. Create agent service in `app/services/`
2. Create agent definition in `app/agents/`
3. Wrap as tool in `app/agents/supervisor.py`
4. Test via chat API

### Option B: Enhance Existing Agents

1. Add more tools to competitor monitoring agent
2. Improve memory management
3. Add more sophisticated analysis

### Option C: Frontend Integration

1. Connect Next.js frontend to chat API
2. Implement real-time streaming UI
3. Add HITL approval interface
4. Build monitoring dashboard

## 🎯 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Multi-Agent System | ✅ Complete | Subagents pattern implemented |
| Supervisor Agent | ✅ Working | Routes to specialized agents |
| Competitor Monitoring | ✅ Working | Research & monitoring setup |
| Chat API | ✅ Complete | Single turn + streaming |
| HITL Support | ✅ Complete | Approval workflows |
| Firestore | ✅ Complete | User configs + monitoring data |
| Firebase Auth | ✅ Complete | User authentication |
| Cron Jobs | ✅ Complete | Scheduled monitoring |
| Content Planning Agent | ⏳ TODO | Your teammates can add |
| Publishing Agent | ⏳ TODO | Your teammates can add |

## 💡 Pro Tips

1. **Check Swagger docs**: http://localhost:8000/docs for all available endpoints
2. **Test with thread IDs** to maintain conversation context across multiple messages
3. **Use streaming** for better UX with long-running agent operations
4. **Follow AGENT_DEVELOPER_GUIDE.md** when adding new agents - it prevents conflicts
5. **Supervisor handles routing** automatically - no need to specify which agent
6. **Services can be called directly** from cron jobs or other services (bypassing supervisor)

Your multi-agent system is fully operational and ready for expansion! 🎉
