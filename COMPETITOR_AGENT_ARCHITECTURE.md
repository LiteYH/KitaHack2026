# Competitor Monitoring Agent — Technical Architecture

> **BossolutionAI** · KitaHack 2026 · Google Hackathon
>
> An AI-powered competitive intelligence system for SMEs, built on **Google Gemini**, **LangGraph**, and **Firebase**.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Agent Hierarchy](#3-agent-hierarchy)
4. [Competitor Monitoring Agent — Deep Dive](#4-competitor-monitoring-agent--deep-dive)
5. [Tools Layer](#5-tools-layer)
6. [Skills System (Progressive Disclosure)](#6-skills-system-progressive-disclosure)
7. [HITL (Human-in-the-Loop) Approval Flow](#7-hitl-human-in-the-loop-approval-flow)
8. [Continuous Monitoring & Cron Pipeline](#8-continuous-monitoring--cron-pipeline)
9. [Streaming & API Layer](#9-streaming--api-layer)
10. [Data Layer (Firebase / Firestore)](#10-data-layer-firebase--firestore)
11. [Frontend Integration](#11-frontend-integration)
12. [Key Technology Choices](#12-key-technology-choices)
13. [End-to-End Flow Walkthrough](#13-end-to-end-flow-walkthrough)

---

## 1. System Overview

BossolutionAI's Competitor Monitoring Agent delivers real-time competitive intelligence to SME owners through a conversational interface. The agent:

- **Researches** competitors on demand via web search (Tavily API)
- **Analyses** findings with skill-guided LLM reasoning
- **Creates** continuous monitoring jobs with HITL approval
- **Notifies** users of significant competitor changes via email
- **Renders** structured insights as Generative UI cards in the chat

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND  (Next.js 15)                          │
│  /chat  →  ChatArea  →  SSE Stream  →  GenUI Renderer / HITL Cards       │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │  HTTP + SSE
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         BACKEND  (FastAPI + Python)                      │
│                                                                           │
│   POST /api/v1/chat/stream          ← user messages                      │
│   POST /api/v1/chat/resume          ← HITL decisions                     │
│   GET  /api/v1/crons                ← monitoring job list                 │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Multi-Agent Service                              │  │
│  │                                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │              SUPERVISOR AGENT  (Gemini 2.5 Flash)            │  │  │
│  │  │   • Routes user intent                                        │  │  │
│  │  │   • Delegates to subagents as tools                          │  │  │
│  │  │   • MemorySaver (per conversation thread)                    │  │  │
│  │  └───────────────────────┬──────────────────────────────────────┘  │  │
│  │                           │ tool call                                │  │
│  │  ┌────────────────────────▼─────────────────────────────────────┐  │  │
│  │  │         COMPETITOR MONITORING AGENT  (Gemini 3 Flash)        │  │  │
│  │  │   • Web research (Tavily)                                     │  │  │
│  │  │   • Monitoring CRUD + HITL                                    │  │  │
│  │  │   • Skill-based progressive disclosure                       │  │  │
│  │  │   • InMemorySaver (per subagent thread)                      │  │  │
│  │  └───────────┬───────────────────────────────────────────────────┘  │  │
│  └──────────────┼────────────────────────────────────────────────────┘  │
│                 │                                                         │
│     ┌───────────▼──────────┐   ┌──────────────────┐  ┌───────────────┐  │
│     │   Tavily Search API  │   │  CronService      │  │  Firestore    │  │
│     │   (real-time web)    │   │  (APScheduler)    │  │  (persistence)│  │
│     └──────────────────────┘   └──────────────────┘  └───────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                        ┌─────────▼──────────┐
                        │  Firebase / GCP     │
                        │  Auth · Firestore   │
                        │  Storage            │
                        └─────────────────────┘
```

---

## 3. Agent Hierarchy

```
SUPERVISOR (BossolutionAI)
│
│  Receives all user messages
│  Uses a routing system-prompt to decide:
│    ├── Answer directly (marketing advice, general questions)
│    └── Delegate to subagent tool
│
└─── COMPETITOR MONITORING AGENT  ← current spec
     (invoked as a @tool inside the supervisor)
     │
     ├── search_competitor         (Tavily web search)
     ├── search_competitor_news    (Tavily news search)
     ├── create_monitoring_config  (HITL → CronService)
     ├── update_monitoring_config  (HITL → CronService)
     └── check_user_competitors    (Firestore read)
```

The supervisor wraps the competitor agent via a LangChain `@tool` decorated async function. A **deterministic subagent thread ID** is derived from the supervisor's `thread_id` so the subagent's checkpoint persists correctly across the interrupt–resume HITL cycle.

---

## 4. Competitor Monitoring Agent — Deep Dive

### Source
`backend/app/agents/competitor_monitoring/agent.py`

### Construction Pipeline

```
create_competitor_monitoring_agent()
  │
  ├── 1. LLM: ChatGoogleGenerativeAI("gemini-3-flash-preview", temperature=0.3)
  │
  ├── 2. Skills (Middleware)
  │       SkillLoader  ──reads──▶  /skills/{name}/*.md
  │       SkillMiddleware          Skills: competitor_search
  │                                        competitor_analysis
  │                                        generative_ui
  │
  ├── 3. Summarization Middleware
  │       SummarizationMiddleware(
  │           model = "gemini-2.5-flash",
  │           trigger = ("tokens", 80_000),   # condense when near limit
  │           keep   = ("messages", 15),       # keep last 15 messages
  │       )
  │
  ├── 4. Tools
  │       search_competitor
  │       search_competitor_news
  │       create_monitoring_config
  │       update_monitoring_config
  │       check_user_competitors
  │
  └── 5. Graph: create_agent(model, tools, checkpointer=InMemorySaver())
```

### Memory Model

| Layer | Type | Scope |
|---|---|---|
| Supervisor | `MemorySaver` | Persists full conversation per `thread_id` |
| Competitor Agent | `InMemorySaver` | Scoped to one subagent invocation thread |
| Long-term context | `SummarizationMiddleware` | Compresses history exceeding 80k tokens |

---

## 5. Tools Layer

### `search_competitor`
**File:** `tools/search_tools.py`

| Property | Value |
|---|---|
| Provider | Tavily Search API |
| Search depth | `basic` (optimised for 3–5× speed vs. `advanced`) |
| Max results | 3 per aspect |
| Aspects | `products`, `pricing`, `social`, `general` |
| Returns | AI-generated answer + raw search results with URLs |

**Flow:**
```
search_competitor(competitor_name, aspects)
    │
    ├── for each aspect:
    │     build_query(competitor, aspect)  →  Tavily API
    │     receive { answer, results[] }
    │
    └── return aggregated findings dict
```

---

### `search_competitor_news`
**File:** `tools/search_tools.py`

Same as above but constrained to **recent news** queries (past 2 weeks by default). Used when users ask "What's the latest from…?".

---

### `create_monitoring_config`
**File:** `tools/monitoring_tools.py`

Creates a recurring monitoring job. Internally triggers **HITL approval** before activating.

```
create_monitoring_config(
    competitor, aspects, frequency_hours, notification_preference
)
    │
    ├── 1. Build approval payload  (competitor, aspects, schedule preview)
    │
    ├── 2. lg_interrupt(approval_payload)
    │         ─── LangGraph PAUSES the subagent graph ───
    │         ─── Frontend receives {"type":"interrupt", "data":[...]} ───
    │         ─── User approves / rejects on HITL card ───
    │         ─── Frontend POSTs /chat/resume ───
    │         ─── LangGraph RESUMES with user decision ───
    │
    ├── 3. If approved:
    │       CronService.create_monitoring_job(...)
    │       Firestore: competitors/{user_id}/{config_id}  ← write config
    │
    └── 4. Return { config_id, job_id, frequency_label, status: "active" }
```

---

### `update_monitoring_config`
**File:** `tools/monitoring_tools.py`

Updates an existing monitoring job's frequency or aspects. Also HITL-gated.

---

### `check_user_competitors`
**File:** `tools/monitoring_tools.py`

Reads Firestore to list all active monitoring configurations for the current `user_id`. No HITL — read-only.

---

## 6. Skills System (Progressive Disclosure)

Skills are **Markdown knowledge files** loaded dynamically by the agent at runtime, controlled by a `load_skill` meta-tool. This keeps the base system prompt short while giving the agent access to detailed schemas and examples on demand.

```
/skills/
  competitor_search/      ← search query construction, Tavily tips
  competitor_analysis/    ← analysis frameworks, how to interpret data
  generative_ui/          ← GenUI component schemas, [GENUI:...] syntax
  notification_management/
```

**Loading Protocol enforced by system prompt:**
1. Identify what the agent needs to do
2. Call `load_skill(skill_name=…)` FIRST
3. Follow the skill's detailed guidance

**Why this pattern?**
- Avoids bloating the base context window with rarely-used knowledge
- Allows in-context updating of behaviour without redeploying the agent
- Forces explicit intent declaration before generating structured outputs (especially GenUI)

---

## 7. HITL (Human-in-the-Loop) Approval Flow

HITL prevents the agent from creating/modifying monitoring jobs without explicit user consent.

### Sequence

```
User: "Monitor Nike daily"
  │
  ▼
SUPERVISOR  ──tool call──▶  COMPETITOR AGENT
                                  │
                                  ▼
                          create_monitoring_config()
                                  │
                          lg_interrupt(approval_data)
                                  │
                          ◀── GRAPH PAUSED ──▶
                                  │
              SSE event: {"type":"interrupt","data":[{competitor,aspects,...}]}
                                  │
                                  ▼
                          FRONTEND: renders <HITLApprovalCard />
                                  │
                          User clicks APPROVE / REJECT
                                  │
              POST /api/v1/chat/resume  { thread_id, decisions:[{approved:true}] }
                                  │
                                  ▼
                          GRAPH RESUMES → CronService.create_monitoring_job()
                                  │
                                  ▼
              SSE event: {"type":"token","content":"✅ Monitoring activated!..."}
```

### Chained HITL (Multiple Competitors)

When a single request requires approving multiple monitoring jobs, the supervisor implements a **chained HITL** pattern:

1. First interrupt surfaces and pauses the supervisor
2. On resume, the subagent gets forwarded the decision
3. If another interrupt is detected, a `AWAITING_NEXT_APPROVAL` sentinel is returned
4. The supervisor calls `competitor_monitoring` again with a **fresh task** (clean interrupt position 0)
5. Process repeats until all approvals are collected

This avoids the LangGraph position-replay bug where future resume turns would erroneously replay a prior decision into the wrong interrupt slot.

---

## 8. Continuous Monitoring & Cron Pipeline

**File:** `backend/app/services/cron_service.py`

```
CronService (APScheduler — AsyncIOScheduler)
│
├── In-memory job store (MemoryJobStore)
├── Firestore sync for persistence across restarts
│
└── Monitoring Job Execution (every N hours):
      │
      ├── competitor_agent_service.invoke(
      │       f"Research {competitor} for {aspects}",
      │       thread_id=f"cron_{job_id}"
      │   )
      │
      ├── Diff results against last snapshot
      │
      ├── If significant changes AND notification_preference ≠ "never":
      │       ChatHistoryService.save_message(...)   ← stores in Firestore
      │       SMTP email notification to user
      │
      └── Update Firestore: monitoring_results/{job_id}/runs/{runId}
```

### Job Configuration stored in Firestore

```
competitors/{user_id}/{config_id}
  ├── competitor:             "Nike"
  ├── aspects:                ["news", "products"]
  ├── frequency_hours:        24
  ├── notification_preference: "significant_only"
  ├── job_id:                 "job_abc123"
  ├── status:                 "active"
  └── created_at:             <timestamp>
```

---

## 9. Streaming & API Layer

**File:** `backend/app/api/v1/routers/chat.py`

### Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/chat/stream` | Start or continue a conversation (SSE) |
| `POST` | `/api/v1/chat/resume` | Resume after HITL approval |
| `GET` | `/api/v1/crons` | List user's monitoring jobs |
| `DELETE` | `/api/v1/crons/{job_id}` | Cancel a monitoring job |

### SSE Event Schema

```jsonc
// Streaming token
{ "type": "token",     "content": "## Nike Analysis\n..." }

// HITL interrupt — frontend renders approval card
{ "type": "interrupt", "data": [{
    "id": "uuid",
    "value": {
      "competitor": "Nike",
      "aspects": ["news", "products"],
      "frequency_hours": 24,
      "frequency_label": "Daily",
      "notification_preference": "significant_only",
      "message": "Approve setting up daily monitoring for Nike?"
    }
  }]
}

// Stream complete
{ "type": "done" }
```

### Auth Middleware

Every request carries a **Firebase ID Token** in the `Authorization: Bearer <token>` header. `backend/app/core/auth.py` verifies it with the Firebase Admin SDK and injects `user_id` into all service calls.

---

## 10. Data Layer (Firebase / Firestore)

```
Firestore Collections
│
├── users/{userId}
│     └── profile, preferences
│
├── conversations/{userId}/threads/{threadId}/messages/{msgId}
│     └── role, content, timestamp, type, genui_data
│
├── competitors/{userId}/{configId}
│     └── monitoring config (see §8)
│
└── monitoring_results/{jobId}/runs/{runId}
      └── timestamp, findings, diff_summary, notified
```

Firebase Auth manages identity. Firebase Admin SDK (Python) handles server-side token verification.

---

## 11. Frontend Integration

### Components

| Component | File | Purpose |
|---|---|---|
| `AgentChatArea` | `components/chat/agent-chat-area.tsx` | Main chat container, SSE consumer |
| `HITLApprovalCard` | `components/chat/hitl-approval-card.tsx` | Approval / rejection UI for HITL events |
| `GenUIRenderer` | `components/genui/GenUIRenderer.tsx` | Renders structured [GENUI:...] blocks |
| `CronJobsSidebar` | `components/chat/cron-jobs-sidebar.tsx` | Lists active monitoring jobs |
| `ToolCallBubble` | `components/chat/tool-call-bubble.tsx` | Shows in-progress tool invocations |

### GenUI Components (rendered from agent output)

| Component | Description |
|---|---|
| `CompetitorComparisonCard` | Side-by-side brand comparison |
| `MetricsCard` | KPI snapshot with trend indicators |
| `TrendChart` | Time-series chart for tracked metrics |
| `InsightCard` | Text insight with severity rating |
| `FeatureComparisonTable` | Feature matrix across competitors |

The agent outputs `[GENUI: <ComponentName> {...json props}]` markers inside its response text. `GenUIRenderer` parses these and renders the React components inline.

### Hook: `useAgentChat`
**File:** `hooks/use-agent-chat.ts`

Manages the SSE connection lifecycle, accumulates streaming tokens, handles `interrupt` events by pushing an approval card into the message list, and sends resume payloads on user decision.

---

## 12. Key Technology Choices

| Technology | Role | Why |
|---|---|---|
| **Google Gemini 2.5 Flash** | Supervisor LLM | Fast, cost-efficient, strong instruction-following |
| **Google Gemini 3 Flash Preview** | Competitor agent LLM | Latest multimodal reasoning, structured output |
| **LangGraph** | Agent orchestration | First-class interrupt/resume for HITL, graph-based state |
| **LangChain** | Tool/middleware framework | `@tool` decorators, middleware pipeline, `create_agent` |
| **Tavily Search API** | Real-time web search | Purpose-built for LLM agents, structured JSON responses |
| **APScheduler** | Cron job execution | Lightweight async scheduler, no Redis required for MVP |
| **Firebase Auth** | Identity | Zero-friction Google Sign-In, ID token verification |
| **Firestore** | Persistence | Real-time sync, no-schema, scales to hackathon demo load |
| **FastAPI** | REST + SSE server | Async-native, automatic OpenAPI docs |
| **Next.js 15** | Frontend | App Router, RSC, TypeScript |

---

## 13. End-to-End Flow Walkthrough

### Scenario: "Monitor Adidas daily and tell me what they're up to"

```
1. User types message in /chat
   └─▶ POST /api/v1/chat/stream  { message, thread_id }

2. Supervisor receives message
   └─▶ Decides: needs competitor research + monitoring setup
   └─▶ Calls competitor_monitoring tool with:
         "Research Adidas recent activities AND set up daily monitoring for Adidas"

3. Competitor Agent runs:
   a. load_skill("competitor_search")
   b. search_competitor("Adidas", ["products","pricing","social","general"])
      └─▶ Tavily API → returns structured findings
   c. load_skill("competitor_analysis")
   d. Generates analysis + [GENUI: InsightCard {...}] blocks
   e. create_monitoring_config("Adidas", ["news","products"], 24, "significant_only")
      └─▶ lg_interrupt(approval_payload)   ← GRAPH PAUSES

4. SSE stream sends:
   {"type":"token","content":"## Adidas Overview\n..."}   (analysis)
   {"type":"interrupt","data":[{competitor:"Adidas",...}]} (HITL card)

5. Frontend renders:
   - Adidas analysis with InsightCard GenUI component
   - HITLApprovalCard: "Approve daily monitoring for Adidas?"

6. User clicks APPROVE
   └─▶ POST /api/v1/chat/resume  { thread_id, decisions:[{approved:true}] }

7. Graph resumes in competitor agent:
   └─▶ CronService.create_monitoring_job("Adidas", ["news","products"], 24h, user_id)
       └─▶ Job stored in Firestore + APScheduler queue
   └─▶ Returns confirmation string to supervisor

8. Supervisor synthesises + streams final response:
   {"type":"token","content":"✅ Monitoring activated! Adidas is now tracked daily.\nJob ID: job_xyz"}
   {"type":"done"}

9. Every 24h thereafter:
   └─▶ APScheduler fires → competitor_agent_service.invoke("Research Adidas news/products")
   └─▶ New findings stored → significant changes → email notification sent to user
```

---

*Built for KitaHack 2026 · Powered by Google Gemini · © BossolutionAI Team*
