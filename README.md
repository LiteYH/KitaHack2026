# BossolutionAI

**AI-Powered Marketing Intelligence Platform for SMEs**

Built for KitaHack 2026  an end-to-end multi-agent system that helps small businesses automate competitor research, plan content, optimise campaigns, and track ROI via a conversational interface.

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-blueviolet?style=flat)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=flat&logo=google)](https://ai.google.dev)
[![Firebase](https://img.shields.io/badge/Firebase-Auth_+_Firestore-orange?style=flat&logo=firebase)](https://firebase.google.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=flat&logo=python)](https://python.org)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Multi-Agent System](#multi-agent-system)
- [HITL Approval Flow](#hitl-approval-flow)
- [Continuous Monitoring](#continuous-monitoring)
- [Generative UI](#generative-ui)
- [Team](#team)

---

## Overview

BossolutionAI is a full-stack AI assistant designed for SME marketing teams. Unlike generic chatbots, it uses a **multi-agent LangGraph architecture** where a Supervisor Agent orchestrates specialised subagents  each with its own tools, skills, and memory. All agent reasoning is streamed live to the user via Server-Sent Events (SSE), and the system supports **Human-in-the-Loop (HITL)** approval gates so no automated action is ever taken without user consent.

```
User -> /chat -> Supervisor Agent (Gemini 2.5 Flash)
                    +-- Competitor Monitoring Agent  (Tavily search + cron jobs + HITL)
                    +-- Content Planning Agent       (Gemini image gen + calendar)
                    +-- Campaign Optimisation Tool   (Firestore campaigns + ROI)
                    +-- ROI Analysis Tool            (charts + PDF report)
```

---

## Features

### Competitor Intelligence
- **Live web research** via Tavily Search API across products, pricing, social media, and news
- **Automated monitoring jobs** (APScheduler) that run every N hours and diff results
- **Email notifications** when significant competitor changes are detected
- **HITL approval gates** before any monitoring job is created or modified
- **GenUI insight cards** rendered inline in the chat from structured agent output

### Content Planning
- AI-generated content calendars tailored to your brand
- Platform-specific copy suggestions (Instagram, Facebook, LinkedIn, Twitter)
- Scheduled content with visual previews
- Image generation via Google Imagen API

### Campaign Optimisation
- Create and manage marketing campaigns stored in Firestore
- Platform-specific performance breakdown (CPC, CTR, ROAS, conversion rate)
- Budget vs. spend tracking with status indicators (active / paused / completed)
- AI recommendations for campaigns to scale or pause

### ROI Analysis
- Revenue, cost, net profit, and ROI charts embedded directly in chat
- Filter by last 7 / 30 / 90 days
- One-click **PDF report** download with AI-generated insights
- Charts persist on the message they were generated with

### Conversational Interface
- Full chat with message history persisted in Firestore
- Real-time SSE token streaming with live tool call / tool result bubbles
- Agent status indicators showing which subagent is currently active
- Collapsible tool output panels for full transparency

### Authentication
- Firebase Email/Password and Google Sign-In
- Protected routes with AuthContext
- Password reset flow

---

## Architecture

```
+-------------------------------------------------------------+
|                  FRONTEND  (Next.js 15)                      |
|  /chat --SSE--> useAgentChat hook --> AgentChatArea          |
|                      |                        |              |
|                MessageBubble            HITLApprovalCard     |
|                ToolCallBubble           GenUIRenderer        |
|                ROIChart                 CronJobsSidebar      |
+-------------------------+-----------------------------------+
                          | HTTP + SSE (Firebase ID Token)
                          v
+-------------------------------------------------------------+
|                  BACKEND  (FastAPI + Python)                  |
|                                                              |
|  POST /api/v1/chat/stream     POST /api/v1/chat/resume       |
|  GET  /api/v1/campaigns       GET  /api/v1/crons             |
|  GET  /api/v1/roi             POST /api/v1/roi/report        |
|                                                              |
|  +---------------------------------------------------+       |
|  |          MultiAgentService (stream + save)        |       |
|  |                                                   |       |
|  |  +---------------------------------------------+ |       |
|  |  |   SUPERVISOR AGENT  (Gemini 2.5 Flash)      | |       |
|  |  |   MemorySaver -- persists per thread_id     | |       |
|  |  +-------------------+-------------------------+ |       |
|  |                      | tool calls               |       |
|  |   +-----------------+v-+  +------------------+  |       |
|  |   | Competitor Agent   |  | Content Planner  |  |       |
|  |   | (Gemini 3 Flash)   |  | (Gemini 2.5)     |  |       |
|  |   | Tavily + APSched   |  | Imagen API       |  |       |
|  |   +--------------------+  +------------------+  |       |
|  +---------------------------------------------------+       |
|                                                              |
|  Firestore . Firebase Auth . APScheduler . SMTP             |
+-------------------------------------------------------------+
```

---

## Tech Stack

### Frontend

| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript 5.7 |
| Styling | Tailwind CSS 4 + Radix UI |
| Auth | Firebase SDK 10 |
| State | React Context + useAgentChat hook |
| Charts | Recharts (ROI visualisation) |
| Streaming | Native EventSource / SSE |

### Backend

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.119 + Uvicorn |
| Language | Python 3.10+ |
| AI Orchestration | LangGraph + LangChain |
| LLM | Google Gemini 2.5 Flash (supervisor) / Gemini 3 Flash (subagents) |
| Web Search | Tavily Search API |
| Scheduler | APScheduler (AsyncIOScheduler) |
| Image Gen | Google Imagen API (via Gemini) |
| Validation | Pydantic v2 |

### Infrastructure

| Layer | Technology |
|---|---|
| Auth | Firebase Authentication |
| Database | Firestore (NoSQL) |
| Storage | Firebase Storage |
| PDF Reports | xhtml2pdf |
| Email | SMTP (dotenv-configured) |

---

## Project Structure

```
KitaHack2026/
|
+-- frontend/                          Next.js application
|   +-- app/
|   |   +-- auth/                      Sign in / sign up / forgot-password
|   |   +-- chat/                      Main chat dashboard (protected)
|   |   +-- cron-jobs/                 Monitoring jobs page (protected)
|   |
|   +-- components/
|   |   +-- chat/
|   |   |   +-- agent-chat-area.tsx    Main SSE consumer + message renderer
|   |   |   +-- message-bubble.tsx     Markdown + GenUI + ROI chart renderer
|   |   |   +-- hitl-approval-card.tsx HITL approve/reject card
|   |   |   +-- tool-call-bubble.tsx   Live tool invocation display
|   |   |   +-- tool-result-bubble.tsx Tool response display
|   |   |   +-- cron-jobs-sidebar.tsx  Active monitoring jobs list
|   |   |   +-- campaign-analytics-card.tsx  Campaign metrics table
|   |   |   +-- roi-chart.tsx          Recharts ROI chart component
|   |   +-- genui/
|   |   |   +-- GenUIRenderer.tsx      Parses [GENUI:...] -> React components
|   |   +-- ui/                        Radix-based shadcn components
|   |
|   +-- hooks/
|   |   +-- use-agent-chat.ts          SSE lifecycle, message state, HITL
|   |
|   +-- lib/
|       +-- firebase.ts                Firebase client init
|       +-- api/
|           +-- agent.ts               Typed SSE event definitions
|           +-- campaign.ts            Campaign API calls
|           +-- report.ts              PDF report download
|
+-- backend/
|   +-- main.py                        FastAPI app entry point
|   |
|   +-- app/
|   |   +-- core/
|   |   |   +-- config.py              Pydantic settings (env vars)
|   |   |   +-- firebase.py            Firebase Admin SDK init
|   |   |   +-- auth.py                Token verification middleware
|   |   |
|   |   +-- api/v1/routers/
|   |   |   +-- chat.py                /chat/stream  /chat/resume
|   |   |   +-- campaigns.py           /campaigns CRUD
|   |   |   +-- crons.py               /crons list + delete
|   |   |   +-- roi.py                 /roi analysis + report
|   |   |   +-- youtube_report.py      /youtube-report
|   |   |
|   |   +-- agents/
|   |   |   +-- supervisor.py          Supervisor agent + all tool wrappers
|   |   |   +-- competitor_monitoring/
|   |   |       +-- agent.py           Competitor monitoring agent factory
|   |   |       +-- tools/
|   |   |       |   +-- search_tools.py      search_competitor, search_news
|   |   |       |   +-- monitoring_tools.py  create/update/check config
|   |   |       +-- skills/            Markdown knowledge files
|   |   |           +-- competitor_search/
|   |   |           +-- competitor_analysis/
|   |   |           +-- generative_ui/
|   |   |           +-- notification_management/
|   |   |
|   |   +-- services/
|   |       +-- multi_agent_service.py      SSE streaming + event persistence
|   |       +-- competitor_agent_service.py Standalone invocation (for crons)
|   |       +-- cron_service.py             APScheduler job management
|   |       +-- monitoring_service.py       Diff + email notification logic
|   |       +-- rag_service.py              RAG over social media dataset
|   |       +-- chat_history_service.py     Firestore message persistence
|   |       +-- roi_tool.py                 ROI calculation + chart generation
|   |
|   +-- scripts/                       Dev / seed utilities
|       +-- seed_campaigns.py
|       +-- seed_mock_data.py
|       +-- fix_campaign_userid.py
|
+-- COMPETITOR_AGENT_ARCHITECTURE.md   Deep-dive agent architecture doc
+-- DEMO_SCRIPT_COMPETITOR_MONITORING.md  1-minute demo script
+-- README.md
```

---

## Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.10+
- Firebase project with Firestore and Authentication enabled
- Google Cloud project with Gemini API access
- Tavily API key (competitor web search)

### 1. Clone

```bash
git clone https://github.com/your-org/bossolutionai.git
cd bossolutionai
```

### 2. Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys (see Environment Variables below)

# Start API server
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
pnpm install
cp .env.local.example .env.local
# Edit .env.local with your Firebase config
pnpm dev
```

### 4. Open

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

### 5. Seed demo data (optional)

```bash
cd backend
python scripts/seed_campaigns.py    # 9 fashion brand campaigns
python scripts/seed_mock_data.py    # social media performance records
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key

# Tavily (competitor web search)
TAVILY_API_KEY=your_tavily_api_key

# Firebase Admin SDK
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token

# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_FROM_EMAIL=noreply@bossolutionai.com
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## API Reference

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/chat/stream | Start or continue a conversation (SSE) |
| POST | /api/v1/chat/resume | Resume after HITL approval |

**POST /api/v1/chat/stream** body:

```json
{
  "message": "What is Nike doing on social media?",
  "thread_id": "uuid-from-client",
  "user_email": "user@example.com"
}
```

SSE event types:

```jsonc
{ "type": "token",       "content": "## Nike Overview..." }
{ "type": "tool_call",   "name": "search_competitor", "args": {...} }
{ "type": "tool_result", "name": "search_competitor", "content": "...", "charts": [...] }
{ "type": "agent_status","node": "competitor_monitoring" }
{ "type": "interrupt",   "data": [{ "id": "...", "value": { "competitor": "Nike", ... } }] }
{ "type": "done" }
{ "type": "error",       "message": "..." }
```

**POST /api/v1/chat/resume** body:

```json
{ "thread_id": "uuid", "decisions": [{ "approved": true }] }
```

### Campaigns

| Method | Endpoint | Description |
|---|---|---|
| GET    | /api/v1/campaigns?user_id=... | List campaigns for a user |
| POST   | /api/v1/campaigns             | Create a campaign |
| PUT    | /api/v1/campaigns/{id}        | Update a campaign |
| DELETE | /api/v1/campaigns/{id}        | Delete a campaign |

### Cron / Monitoring Jobs

| Method | Endpoint | Description |
|---|---|---|
| GET    | /api/v1/crons?user_id=... | List monitoring jobs |
| DELETE | /api/v1/crons/{job_id}    | Cancel a job |

### ROI

| Method | Endpoint | Description |
|---|---|---|
| GET  | /api/v1/roi?user_email=...&days=30 | ROI data + charts |
| POST | /api/v1/roi/report                 | Generate PDF report |

All endpoints require `Authorization: Bearer <firebase_id_token>`.

---

## Multi-Agent System

### Supervisor Agent
- Model: `gemini-2.5-flash-preview`
- Checkpointer: `MemorySaver`  conversation persists across messages per `thread_id`
- Routing: Analyses user intent and delegates to the correct subagent or answers directly
- Subagent tools: `competitor_monitoring`, `content_planner`, `roi_analysis`, `campaign_insights`

### Competitor Monitoring Agent
- Model: `gemini-3-flash-preview`
- Checkpointer: `InMemorySaver`  stateless across supervisor invocations
- Middleware: `SkillMiddleware` (on-demand knowledge loading) + `SummarizationMiddleware` (80k token trigger, keeps last 15 messages)
- Tools: `search_competitor`, `search_competitor_news`, `create_monitoring_config`, `update_monitoring_config`, `check_user_competitors`

### Skills System

Skills are Markdown knowledge files loaded on-demand by the agent via a `load_skill` meta-tool. This keeps the base context window compact while letting the agent access detailed schemas and examples when needed.

```
skills/
  competitor_search/       query construction, Tavily tips
  competitor_analysis/     analysis frameworks, insight templates
  generative_ui/           GenUI component schemas + [GENUI:...] syntax
  notification_management/ email preference handling
```

---

## HITL Approval Flow

```
User: "Monitor Adidas daily"
  |
  v
Competitor Agent calls create_monitoring_config()
  |
  v
lg_interrupt(approval_payload)  ->  LangGraph PAUSES
  |
  v
SSE: { "type": "interrupt", "data": [{ competitor, aspects, schedule }] }
  |
  v
Frontend renders HITLApprovalCard
  |
User clicks APPROVE
  |
  v
POST /api/v1/chat/resume  { decisions: [{ approved: true }] }
  |
  v
Graph RESUMES -> CronService.create_monitoring_job() -> Firestore write
  |
  v
SSE: { "type": "token", "content": "Monitoring activated for Adidas..." }
```

Multiple competitors in one message each trigger their own sequential HITL card via a chained approval pattern that avoids the LangGraph position-replay bug.

---

## Continuous Monitoring

Once approved, jobs run autonomously on the configured schedule:

1. **APScheduler** fires job every `frequency_hours`
2. `CompetitorAgentService` runs a fresh web research pass
3. Results are **diffed** against the last snapshot
4. If significant changes detected and `notification_preference != "never"`:
   - Insight saved to Firestore chat history (visible next login)
   - Email notification sent via SMTP
5. Run logged to `monitoring_results/{job_id}/runs/{runId}`

Firestore schema:

```
competitors/{userId}/{configId}
  competitor:              "Adidas"
  aspects:                 ["news", "products"]
  frequency_hours:         24
  notification_preference: "significant_only"
  status:                  "active"
  job_id:                  "job_abc123"
```

---

## Generative UI

Agents output `[GENUI: ComponentName {...json}]` markers inline with their text. `GenUIRenderer` parses these and renders interactive React components directly in the chat bubble.

| Component | Description |
|---|---|
| CompetitorComparisonCard | Side-by-side brand comparison |
| MetricsCard | KPI snapshot with delta indicators |
| TrendChart | Time-series performance chart |
| InsightCard | Text insight with severity level |
| FeatureComparisonTable | Feature matrix across competitors |
| ROIChart | Revenue / cost / profit bar chart |
| CampaignAnalyticsCard | Campaign performance metrics table |

---

## Development

```bash
# Backend (hot reload)
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && pnpm dev

# Lint
cd frontend && pnpm lint
```

On Windows, set `$env:PYTHONUTF8="1"` before running Python to avoid Unicode encoding errors in the terminal.

---

## Team

Built for **KitaHack 2026**  Google Hackathon Malaysia.

| Member | Focus Area |
|---|---|
| Ng Zheng Jie | Competitor Monitoring Agent, HITL, Cron Pipeline, LangGraph architecture |

---

## Acknowledgements

- **Google Gemini**  LLM backbone for all agents
- **LangGraph / LangChain**  Multi-agent orchestration and tool framework
- **Tavily**  Real-time web search for competitor research
- **Firebase**  Auth, Firestore, and Storage
- **Next.js**  React framework with App Router
- **FastAPI**  Async Python REST + SSE server
- **APScheduler**  Lightweight cron job execution
- **Radix UI / shadcn**  Accessible component library
- **Recharts**  ROI chart rendering

---

*KitaHack 2026  BossolutionAI  Powered by Google Gemini*
