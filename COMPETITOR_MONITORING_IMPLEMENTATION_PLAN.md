# Competitor Monitoring & Continuous Monitoring Implementation Plan

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Agent Skills System](#agent-skills-system)
3. [Multi-Agent System](#multi-agent-system)
4. [Memory & Persistence Strategy](#memory--persistence-strategy)
5. [Human-in-the-Loop (HITL) Implementation](#human-in-the-loop-hitl-implementation)
6. [Streaming Implementation](#streaming-implementation)
7. [Cron Job Management](#cron-job-management)
8. [GenUI Response Formatting](#genui-response-formatting)
9. [Implementation Phases](#implementation-phases)
10. [Technical Stack](#technical-stack)
11. [File Structure](#file-structure)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (Next.js/React)                    │
│  - Chat Interface with SSE Streaming                         │
│  - HITL Approval Cards (Approve/Edit/Reject)                 │
│  - Cron Jobs Management Sidebar (/app/cron-jobs)            │
│  - GenUI Components (Cards, Tables, Timelines)              │
└────────────────────┬────────────────────────────────────────┘
                     │ SSE (Server-Sent Events)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                        │
│  - /api/v1/chat/stream (SSE endpoint)                       │
│  - /api/v1/crons/* (CRUD endpoints)                         │
│  - /api/v1/monitoring/* (monitoring management)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator Agent (LangChain)                  │
│  - Routes requests to specialized agents                     │
│  - Uses simple classification (no complex routing)           │
│  - Returns structured routing decision                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Competitor Monitoring Agent (LangChain)              │
│  - Agent Skills: Search, Analyze, Notify                    │
│  - Tools: Tavily Search, Google Grounding                   │
│  - HITL Middleware for monitoring approval                   │
│  - GenUI Middleware for rich responses                      │
│  - Firestore Memory Middleware                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Background Services                             │
│  - APScheduler (Dynamic Cron Jobs)                          │
│  - Gmail API (Email Notifications)                          │
│  - Monitoring Task Executor                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Firebase/Firestore                              │
│  - agent_memory (cross-thread memory)                       │
│  - chat_threads (conversation checkpoints)                   │
│  - monitoring_configs (job configurations)                   │
│  - monitoring_results (historical data)                      │
│  - cron_jobs (scheduler metadata)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Skills System

### What are Agent Skills?

Based on Anthropic's Agent Skills specification and LangChain's implementation:

**Agent Skills** are:
- **Progressive disclosure systems**: Only loaded when the agent determines they're useful
- **Folder-based**: Each skill is a directory with a `SKILL.md` file
- **Domain-specific expertise**: Bundle related capabilities with instructions
- **Token-efficient**: Agent reads frontmatter first, loads full content when needed

### Skill Structure

```
backend/app/agents/skills/
├── competitor_search/
│   ├── SKILL.md                 # Main skill instructions
│   ├── search_strategies.md     # Reference docs
│   └── examples/                # Example outputs
│       ├── product_launch.json
│       ├── pricing_analysis.json
│       └── social_sentiment.json
│
├── competitor_analysis/
│   ├── SKILL.md
│   ├── analysis_frameworks.md
│   └── significance_detection.md
│
└── notification_management/
    ├── SKILL.md
    ├── email_templates/
    │   ├── significant_change.html
    │   └── weekly_summary.html
    └── notification_rules.md
```

### SKILL.md Format

Based on Anthropic's specification:

```markdown
---
name: competitor-search
description: |
  Advanced competitor research using Tavily search and Google Grounding.
  Use this skill when the user wants to research competitors, monitor
  market changes, or track specific companies.
license: MIT
---

## When to use this skill

Use this skill when:
- User mentions "monitor [company]" or "track [competitor]"
- Researching competitor activities
- Analyzing market positioning
- Setting up continuous monitoring

## How to use this skill

1. **Identify the target competitor** from user request
2. **Determine monitoring aspects** (products, pricing, social, news)
3. **Execute multi-source search**:
   - Tavily for recent news and updates
   - Google Search with grounding for comprehensive coverage
4. **Load analysis framework** from `analysis_frameworks.md`
5. **Detect significance** using rules in `significance_detection.md`

## Available Sub-capabilities

- `search_news`: Recent news mentions (last 7 days)
- `search_products`: Product launches and updates
- `search_pricing`: Pricing changes and promotions
- `search_social`: Social media sentiment analysis
- `analyze_significance`: Determine if findings are significant

## Output Format

Return structured data following `examples/product_launch.json` format.

## Keywords

competitor, monitor, track, market research, competitive intelligence,
competitor analysis, market monitoring
```

### Implementation in LangChain 1.0

**NOT using Deep Agents** (too heavyweight), but custom skill system:

```python
# backend/app/agents/skills/skill_loader.py
from pathlib import Path
from typing import Dict, List
import frontmatter

class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills_index = self._load_skills_index()
    
    def _load_skills_index(self) -> List[Dict]:
        """Load skill frontmatter for progressive disclosure"""
        skills = []
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    with open(skill_file, 'r') as f:
                        post = frontmatter.load(f)
                        skills.append({
                            'name': post['name'],
                            'description': post['description'],
                            'keywords': post.get('keywords', '').split(', '),
                            'path': skill_dir
                        })
        return skills
    
    def get_relevant_skills(self, query: str) -> List[str]:
        """Progressive disclosure: find relevant skills based on query"""
        relevant = []
        query_lower = query.lower()
        
        for skill in self.skills_index:
            # Check if query matches skill keywords
            if any(kw in query_lower for kw in skill['keywords']):
                # Load full skill content
                skill_file = skill['path'] / "SKILL.md"
                with open(skill_file, 'r') as f:
                    post = frontmatter.load(f)
                    relevant.append(post.content)
        
        return relevant
```

### Skills as Middleware

Convert skills to tools that the agent can invoke:

```python
# backend/app/agents/skills/skill_tools.py
from langchain.tools import tool
from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
def competitor_search_skill(request, handler):
    """
    Wraps search tool with competitor-specific expertise.
    Loads search strategies and examples when invoked.
    """
    skill_loader = SkillLoader(Path("app/agents/skills"))
    strategies = skill_loader.load_skill_content("competitor_search")
    
    # Enhance request with skill context
    enhanced_request = request.with_system_context(strategies)
    return handler(enhanced_request)

@tool
def search_competitor(competitor_name: str, aspect: str) -> dict:
    """
    Search for competitor information using Tavily + Google Grounding.
    
    Args:
        competitor_name: Name of the competitor (e.g., "Nike")
        aspect: What to search for (products, pricing, news, social)
    """
    # This tool is wrapped by competitor_search_skill middleware
    # Implementation uses Tavily Search API + Google Grounding
    pass
```

---

## Multi-Agent System

### 1. Orchestrator Agent

**Purpose**: Simple routing - classifies intent and routes to appropriate agent

**NOT using complex LangGraph routing** - just structured output classification:

```python
# backend/app/agents/orchestrator_agent.py
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Literal

class RoutingDecision(BaseModel):
    """Structured routing decision"""
    agent: Literal[
        "competitor_monitoring",
        "content_planning", 
        "competitor_intelligence",
        "publishing",
        "campaign_optimization",
        "roi_dashboard"
    ] = Field(description="Which agent should handle this request")
    task: str = Field(description="Extracted task description")
    confidence: float = Field(description="Confidence in routing (0-1)")

def create_orchestrator_agent():
    """Simple orchestrator using structured output"""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1
    )
    
    agent = create_agent(
        model=model,
        system_prompt="""You are a marketing assistant orchestrator.
        
        Your ONLY job is to classify the user's request and route it to 
        the appropriate specialized agent.
        
        Routes:
        - competitor_monitoring: "monitor [company]", "track competitor", 
          "set up monitoring", "watch [brand]"
        - competitor_intelligence: "research competitor", "analyze [company]",
          "competitive analysis" (one-time research, NOT continuous monitoring)
        - content_planning: "create content", "plan posts", "content calendar"
        - publishing: "publish", "schedule post", "post to social"
        - campaign_optimization: "optimize campaign", "improve ads", "A/B test"
        - roi_dashboard: "show ROI", "performance metrics", "analytics"
        
        Return a structured routing decision with confidence score.
        If confidence < 0.7, ask the user for clarification.
        """,
        tools=[],  # No tools - just classification
        response_format=RoutingDecision  # Structured output
    )
    
    return agent
```

### 2. Competitor Monitoring Agent

**Purpose**: Handle both one-time research AND continuous monitoring setup

**Uses Agent Skills for enhanced capabilities**:

```python
# backend/app/agents/competitor_monitoring_agent.py
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from .middleware import FirestoreMemoryMiddleware, GenUIMiddleware
from .skills import SkillLoader
from .tools import create_monitoring_tools

def create_competitor_monitoring_agent(
    firestore_client,
    skill_loader: SkillLoader
):
    """
    Agent that handles competitor research and monitoring setup.
    Uses Agent Skills for domain expertise.
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3
    )
    
    # Load skills for this agent
    skills_context = skill_loader.get_skills_summary([
        "competitor_search",
        "competitor_analysis", 
        "notification_management"
    ])
    
    agent = create_agent(
        model=model,
        system_prompt=f"""You are a competitor monitoring specialist.
        
        Your capabilities:
        1. Research competitors (one-time analysis)
        2. Set up continuous monitoring (scheduled tracking)
        
        When setting up monitoring:
        - Ask user for frequency (e.g., "every 2 hours", "daily")
        - Ask what aspects to monitor (products, pricing, news, social)
        - Ask notification preferences (always, significant only, never)
        - Create monitoring configuration
        - Request HITL approval before creating the cron job
        
        Available Skills:
        {skills_context}
        
        Use skills by loading their full content when needed.
        """,
        tools=create_monitoring_tools(skill_loader),
        middleware=[
            # HITL for monitoring approval
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "create_monitoring_config": True,  # Requires approval
                    "search_competitor": False,  # Safe operation
                }
            ),
            # GenUI for rich responses
            GenUIMiddleware(),
            # Firestore for cross-thread memory
            FirestoreMemoryMiddleware(firestore_client)
        ],
        # InMemorySaver for thread-level checkpoints
        checkpointer=InMemorySaver()
    )
    
    return agent
```

### Tools with Skills Integration

```python
# backend/app/agents/tools.py
from langchain.tools import tool
from tavily import TavilyClient
import google.generativeai as genai

def create_monitoring_tools(skill_loader: SkillLoader):
    """Create tools enhanced with agent skills"""
    
    @tool
    def search_competitor(
        competitor_name: str, 
        aspects: List[str]
    ) -> dict:
        """
        Search for competitor information.
        Uses Tavily + Google Grounding enhanced with search skill.
        
        Args:
            competitor_name: Name of competitor (e.g., "Nike")
            aspects: List of aspects to research 
                     (products, pricing, news, social)
        """
        # Load search skill for strategies
        skill_content = skill_loader.load_full_skill("competitor_search")
        
        # Tavily search
        tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = tavily.search(
            query=f"{competitor_name} {' '.join(aspects)}",
            search_depth="advanced",
            max_results=10
        )
        
        # Google Grounding for additional context
        # ... implementation
        
        return {
            "competitor": competitor_name,
            "aspects": aspects,
            "findings": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @tool
    def analyze_significance(findings: dict) -> dict:
        """
        Analyze if findings are significant using skill-based rules.
        Loads significance detection rules from skill.
        """
        skill_content = skill_loader.load_full_skill("competitor_analysis")
        # Apply significance rules
        # ... implementation
        pass
    
    @tool
    def create_monitoring_config(
        competitor: str,
        aspects: List[str],
        frequency_hours: int,
        notification_preference: str
    ) -> dict:
        """
        Create monitoring configuration (triggers HITL).
        
        This tool will trigger Human-in-the-Loop approval.
        """
        config = {
            "competitor": competitor,
            "aspects": aspects,
            "frequency_hours": frequency_hours,
            "notification_preference": notification_preference,
            "created_at": datetime.utcnow().isoformat()
        }
        return config
    
    return [
        search_competitor,
        analyze_significance,
        create_monitoring_config
    ]
```

---

## Memory & Persistence Strategy

### Hybrid Approach: InMemorySaver + Firestore

**Why this approach?**
- ✅ InMemorySaver: Built-in LangChain support, easy to use
- ✅ Firestore: Persistent storage, cross-session memory
- ✅ Best of both worlds: Performance + Persistence

### Architecture

```python
# backend/app/core/memory.py
from langgraph.checkpoint.memory import InMemorySaver
from google.cloud import firestore
from typing import Optional

class HybridMemoryManager:
    """
    Manages both thread-level (InMemorySaver) and 
    cross-thread (Firestore) memory.
    """
    
    def __init__(self, firestore_client: firestore.Client):
        self.checkpointer = InMemorySaver()  # Thread-level
        self.firestore = firestore_client     # Cross-thread
    
    # Thread-level memory (checkpoints)
    async def save_checkpoint(
        self, 
        thread_id: str, 
        state: dict
    ):
        """Save to InMemorySaver, then backup to Firestore"""
        # LangChain handles this automatically via checkpointer
        # But we also backup to Firestore for persistence
        await self.firestore.collection('chat_threads').document(
            thread_id
        ).set({
            'last_checkpoint': state,
            'updated_at': firestore.SERVER_TIMESTAMP
        }, merge=True)
    
    # Cross-thread memory (user preferences, history)
    async def save_user_memory(
        self, 
        user_id: str, 
        memory: dict
    ):
        """Save cross-thread memory to Firestore"""
        await self.firestore.collection('agent_memory').document(
            user_id
        ).set(memory, merge=True)
    
    async def get_user_memory(self, user_id: str) -> dict:
        """Retrieve user's cross-thread memory"""
        doc = await self.firestore.collection('agent_memory').document(
            user_id
        ).get()
        return doc.to_dict() if doc.exists else {}
```

### Firestore Collections Schema

```typescript
// Firestore structure
{
  // Cross-thread memory (persistent across sessions)
  agent_memory: {
    userId: {
      user_preferences: {
        notification_email: string,
        default_frequency: string,
        preferred_aspects: string[]
      },
      monitoring_history: {
        total_jobs_created: number,
        active_competitors: string[]
      },
      conversation_context: {
        last_discussed_competitor: string,
        recent_topics: string[]
      }
    }
  },
  
  // Thread-level checkpoints (backup from InMemorySaver)
  chat_threads: {
    threadId: {
      user_id: string,
      created_at: timestamp,
      last_checkpoint: object,  // Backup of InMemorySaver state
      messages: [
        {
          role: "user" | "assistant",
          content: string,
          timestamp: timestamp
        }
      ]
    }
  },
  
  // Monitoring configurations
  monitoring_configs: {
    configId: {
      user_id: string,
      competitor: string,
      aspects: string[],
      frequency_hours: number,
      notification_preference: "always" | "significant" | "never",
      status: "active" | "paused" | "deleted",
      created_at: timestamp,
      next_run: timestamp,
      apscheduler_job_id: string
    }
  },
  
  // Monitoring results
  monitoring_results: {
    resultId: {
      config_id: string,
      competitor: string,
      execution_time: timestamp,
      findings: object,
      is_significant: boolean,
      significance_score: number,
      notification_sent: boolean,
      raw_data: object
    }
  },
  
  // Cron jobs metadata (synced with APScheduler)
  cron_jobs: {
    jobId: {
      config_id: string,
      apscheduler_id: string,
      status: "running" | "paused" | "failed",
      last_run: timestamp,
      next_run: timestamp,
      error_count: number,
      last_error: string
    }
  }
}
```

### Firestore Memory Middleware

```python
# backend/app/middleware/firestore_memory_middleware.py
from langchain.agents.middleware import AgentMiddleware
from typing import Any, Dict

class FirestoreMemoryMiddleware(AgentMiddleware):
    """
    Middleware to inject user memory from Firestore 
    before each model call.
    """
    
    def __init__(self, firestore_client):
        self.firestore = firestore_client
    
    async def before_model(
        self, 
        state: dict, 
        runtime
    ) -> Optional[Dict[str, Any]]:
        """
        Load user memory from Firestore before model call.
        Inject relevant context.
        """
        user_id = runtime.context.get('user_id')
        if not user_id:
            return None
        
        # Load user memory
        memory = await self._load_user_memory(user_id)
        
        # Inject memory context into system prompt
        memory_context = self._format_memory_context(memory)
        
        return {
            "system_context": memory_context
        }
    
    async def after_model(
        self, 
        state: dict, 
        runtime
    ) -> Optional[Dict[str, Any]]:
        """
        Update user memory in Firestore after model call.
        Extract and save important context.
        """
        # Extract important information from conversation
        # Save to Firestore for future sessions
        pass
    
    async def _load_user_memory(self, user_id: str) -> dict:
        doc = await self.firestore.collection(
            'agent_memory'
        ).document(user_id).get()
        return doc.to_dict() if doc.exists else {}
    
    def _format_memory_context(self, memory: dict) -> str:
        """Format memory for system prompt injection"""
        return f"""
        User Context:
        - Active competitors: {', '.join(memory.get('active_competitors', []))}
        - Preferred notification: {memory.get('notification_preference', 'significant')}
        - Recent topics: {', '.join(memory.get('recent_topics', []))}
        """
```

---

## Human-in-the-Loop (HITL) Implementation

### HITL Flow

```
User: "Monitor Nike"
     ↓
Agent: Gathers requirements (frequency, aspects, notification)
     ↓
Agent: Calls create_monitoring_config tool
     ↓
HITL Middleware: Detects interrupt requirement
     ↓
LangGraph: Saves state, returns interrupt payload
     ↓
Backend: Streams interrupt to frontend via SSE
     ↓
Frontend: Renders approval card with Approve/Edit/Reject buttons
     ↓
User: Reviews and clicks Approve/Edit/Reject
     ↓
Frontend: Sends decision to backend
     ↓
Backend: Resumes agent with Command(resume={decision})
     ↓
Agent: Creates cron job if approved
     ↓
Backend: Confirms creation, streams completion
```

### HITL Middleware Configuration

```python
# backend/app/agents/competitor_monitoring_agent.py
from langchain.agents.middleware import HumanInTheLoopMiddleware

middleware = [
    HumanInTheLoopMiddleware(
        interrupt_on={
            # Require approval with edit capability
            "create_monitoring_config": {
                "allowed_decisions": ["approve", "edit", "reject"],
                "description": "Review monitoring job before creation"
            },
            # Safe operations - no approval needed
            "search_competitor": False,
            "analyze_significance": False,
        },
        description_prefix="🔍 Monitoring Job Approval"
    )
]
```

### HITL Payload Structure

```python
# Interrupt payload sent to frontend
{
    "type": "hitl_interrupt",
    "interrupt_id": "int_abc123",
    "tool_name": "create_monitoring_config",
    "description": "🔍 Monitoring Job Approval",
    "data": {
        "competitor": "Nike",
        "aspects": [
            "product launches",
            "pricing changes", 
            "social media activity"
        ],
        "frequency": "Every 2 hours",
        "frequency_hours": 2,
        "notification_preference": "significant_changes_only",
        "estimated_cost": "$0.05 per execution (~$36/month)",
        "next_run": "2026-02-13T16:00:00Z",
        "timezone": "UTC"
    },
    "actions": ["approve", "edit", "reject"]
}
```

### Frontend HITL Component

```tsx
// frontend/components/chat/hitl-approval-card.tsx
interface HITLApprovalCardProps {
  interrupt: HITLInterrupt;
  onDecision: (decision: HITLDecision) => void;
}

export function HITLApprovalCard({ 
  interrupt, 
  onDecision 
}: HITLApprovalCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState(interrupt.data);
  
  return (
    <Card className="border-amber-500/50 bg-amber-900/10">
      <CardHeader>
        <CardTitle className="text-amber-400 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Monitoring Job Approval Required
        </CardTitle>
        <CardDescription>
          Review the details below before creating this monitoring job
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Competitor */}
        <div>
          <Label>Competitor</Label>
          <div className="font-semibold">{interrupt.data.competitor}</div>
        </div>
        
        {/* Aspects */}
        <div>
          <Label>Monitoring Aspects</Label>
          {isEditing ? (
            <MultiSelect
              value={editedData.aspects}
              onChange={(val) => setEditedData({...editedData, aspects: val})}
              options={[
                'product launches',
                'pricing changes',
                'social media activity',
                'news mentions',
                'job postings'
              ]}
            />
          ) : (
            <div className="flex flex-wrap gap-2 mt-1">
              {interrupt.data.aspects.map(aspect => (
                <Badge key={aspect} variant="secondary">{aspect}</Badge>
              ))}
            </div>
          )}
        </div>
        
        {/* Frequency */}
        <div>
          <Label>Check Frequency</Label>
          {isEditing ? (
            <Select
              value={editedData.frequency_hours}
              onValueChange={(val) => 
                setEditedData({...editedData, frequency_hours: val})
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={1}>Every hour</SelectItem>
                <SelectItem value={2}>Every 2 hours</SelectItem>
                <SelectItem value={6}>Every 6 hours</SelectItem>
                <SelectItem value={12}>Twice daily</SelectItem>
                <SelectItem value={24}>Daily</SelectItem>
              </SelectContent>
            </Select>
          ) : (
            <div className="font-semibold">{interrupt.data.frequency}</div>
          )}
        </div>
        
        {/* Notification Preference */}
        <div>
          <Label>Notify Me</Label>
          {isEditing ? (
            <RadioGroup
              value={editedData.notification_preference}
              onValueChange={(val) => 
                setEditedData({...editedData, notification_preference: val})
              }
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="always" id="always" />
                <Label htmlFor="always">Every time (all results)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="significant" id="significant" />
                <Label htmlFor="significant">
                  Only significant changes (recommended)
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="never" id="never" />
                <Label htmlFor="never">Never (store results only)</Label>
              </div>
            </RadioGroup>
          ) : (
            <div className="font-semibold capitalize">
              {interrupt.data.notification_preference.replace('_', ' ')}
            </div>
          )}
        </div>
        
        {/* Cost Estimate */}
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
          <div className="text-sm text-blue-300">
            💡 Estimated Cost: {interrupt.data.estimated_cost}
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="flex gap-2">
        {isEditing ? (
          <>
            <Button
              onClick={() => {
                onDecision({ type: 'edit', data: editedData });
                setIsEditing(false);
              }}
              className="flex-1"
            >
              <Check className="w-4 h-4 mr-2" />
              Save & Approve
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setEditedData(interrupt.data);
                setIsEditing(false);
              }}
            >
              Cancel
            </Button>
          </>
        ) : (
          <>
            <Button
              onClick={() => onDecision({ type: 'approve' })}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              <Check className="w-4 h-4 mr-2" />
              Approve
            </Button>
            <Button
              variant="outline"
              onClick={() => setIsEditing(true)}
              className="flex-1"
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button
              variant="destructive"
              onClick={() => onDecision({ type: 'reject' })}
              className="flex-1"
            >
              <X className="w-4 h-4 mr-2" />
              Reject
            </Button>
          </>
        )}
      </CardFooter>
    </Card>
  );
}
```

### Backend HITL Handler

```python
# backend/app/api/v1/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langgraph.types import Command

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat endpoint with SSE streaming.
    Handles HITL interrupts.
    """
    
    async def event_generator():
        # Create agent
        agent = create_competitor_monitoring_agent(...)
        
        # Thread configuration
        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "user_id": request.user_id
            }
        }
        
        # Stream with multiple modes
        async for metadata, mode, chunk in agent.astream(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config,
            stream_mode=["messages", "updates"],
            subgraphs=True
        ):
            if mode == "messages":
                # LLM token streaming
                msg, _ = chunk
                if msg.content:
                    yield {
                        "type": "token",
                        "content": msg.content
                    }
            
            elif mode == "updates":
                # Check for HITL interrupt
                if "__interrupt__" in chunk:
                    interrupt_info = chunk["__interrupt__"][0].value
                    
                    # Send interrupt to frontend
                    yield {
                        "type": "hitl_interrupt",
                        "interrupt_id": interrupt_info["id"],
                        "data": interrupt_info["data"],
                        "actions": ["approve", "edit", "reject"]
                    }
                    
                    # Wait for user decision (handled by separate endpoint)
                    break
                
                else:
                    # Regular state update
                    yield {
                        "type": "update",
                        "node": list(chunk.keys())[0],
                        "data": chunk
                    }
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.post("/chat/resume")
async def chat_resume(request: ResumeRequest):
    """
    Resume agent after HITL decision.
    """
    agent = create_competitor_monitoring_agent(...)
    
    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "user_id": request.user_id
        }
    }
    
    # Resume with user decision
    decision_payload = {
        "decisions": [{
            "type": request.decision.type,  # approve/edit/reject
            "data": request.decision.data if hasattr(request.decision, 'data') else None
        }]
    }
    
    async def resume_generator():
        async for metadata, mode, chunk in agent.astream(
            Command(resume=decision_payload),
            config=config,
            stream_mode=["messages", "updates"]
        ):
            # Stream continuation
            if mode == "messages":
                msg, _ = chunk
                if msg.content:
                    yield {"type": "token", "content": msg.content}
            elif mode == "updates":
                yield {"type": "update", "data": chunk}
    
    return StreamingResponse(
        resume_generator(),
        media_type="text/event-stream"
    )
```

---

## Streaming Implementation

### Why SSE (Server-Sent Events)?

**Compared to alternatives:**
- ✅ **SSE**: One-way server → client, simple, built-in browser support
- ❌ **WebSocket**: Bi-directional, more complex, overkill for streaming responses
- ❌ **REST Polling**: Inefficient, high latency

**SSE is perfect for streaming LLM responses** where server sends data to client in real-time.

### SSE Implementation (FastAPI)

```python
# backend/app/api/v1/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE endpoint for streaming chat responses.
    
    Streams:
    - LLM tokens (real-time text generation)
    - State updates (agent progress)
    - HITL interrupts (approval requests)
    - GenUI components (rich cards/tables)
    """
    
    async def event_generator():
        """
        Generator that yields SSE events.
        Format: data: {json}\n\n
        """
        try:
            # Get or create agent
            agent = await get_competitor_agent(request.user_id)
            
            # Configure thread
            config = {
                "configurable": {
                    "thread_id": request.thread_id or f"thread_{uuid.uuid4()}",
                    "user_id": request.user_id
                }
            }
            
            # Stream with multiple modes
            async for metadata, mode, chunk in agent.astream(
                {"messages": [{"role": "user", "content": request.message}]},
                config=config,
                stream_mode=["messages", "updates", "custom"],
                subgraphs=True
            ):
                if mode == "messages":
                    # LLM token streaming
                    msg, metadata = chunk
                    if isinstance(msg, AIMessageChunk) and msg.content:
                        yield {
                            "event": "token",
                            "data": json.dumps({
                                "content": msg.content,
                                "metadata": metadata
                            })
                        }
                
                elif mode == "updates":
                    # State updates or interrupts
                    if "__interrupt__" in chunk:
                        # HITL interrupt
                        interrupt_info = chunk["__interrupt__"][0].value
                        yield {
                            "event": "interrupt",
                            "data": json.dumps({
                                "type": "hitl",
                                "interrupt_id": interrupt_info.get("id"),
                                "tool": interrupt_info.get("tool"),
                                "data": interrupt_info.get("data"),
                                "actions": ["approve", "edit", "reject"]
                            })
                        }
                        break  # Wait for resume
                    
                    else:
                        # Regular state update
                        node_name = list(chunk.keys())[0]
                        yield {
                            "event": "update",
                            "data": json.dumps({
                                "node": node_name,
                                "state": chunk[node_name]
                            })
                        }
                
                elif mode == "custom":
                    # GenUI components from middleware
                    yield {
                        "event": "component",
                        "data": json.dumps(chunk)
                    }
            
            # Send completion
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"})
            }
        
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    # Return SSE response
    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

### Frontend SSE Consumer

```tsx
// frontend/hooks/use-chat-stream.ts
import { useState, useCallback, useRef } from 'react';

interface StreamEvent {
  type: 'token' | 'update' | 'interrupt' | 'component' | 'done' | 'error';
  data: any;
}

export function useChatStream() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [interrupt, setInterrupt] = useState<HITLInterrupt | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  
  const streamMessage = useCallback(async (
    message: string,
    threadId?: string
  ) => {
    setIsStreaming(true);
    setInterrupt(null);
    
    // Add user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Create assistant message (streaming)
    const assistantMessageId = crypto.randomUUID();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      streaming: true
    };
    setMessages(prev => [...prev, assistantMessage]);
    
    try {
      // Create EventSource
      const eventSource = new EventSource(
        `/api/v1/chat/stream?` + new URLSearchParams({
          message,
          threadId: threadId || '',
          userId: getCurrentUserId()
        })
      );
      eventSourceRef.current = eventSource;
      
      // Handle token events
      eventSource.addEventListener('token', (e) => {
        const data = JSON.parse(e.data);
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessageId
            ? { ...msg, content: msg.content + data.content }
            : msg
        ));
      });
      
      // Handle update events
      eventSource.addEventListener('update', (e) => {
        const data = JSON.parse(e.data);
        console.log('Agent update:', data.node);
        // Could show progress indicator
      });
      
      // Handle interrupt events (HITL)
      eventSource.addEventListener('interrupt', (e) => {
        const data = JSON.parse(e.data);
        setInterrupt(data);
        setIsStreaming(false);
        eventSource.close();
      });
      
      // Handle component events (GenUI)
      eventSource.addEventListener('component', (e) => {
        const component = JSON.parse(e.data);
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, components: [...(msg.components || []), component] }
            : msg
        ));
      });
      
      // Handle done event
      eventSource.addEventListener('done', () => {
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, streaming: false }
            : msg
        ));
        setIsStreaming(false);
        eventSource.close();
      });
      
      // Handle error event
      eventSource.addEventListener('error', (e) => {
        console.error('SSE error:', e);
        setIsStreaming(false);
        eventSource.close();
      });
      
    } catch (error) {
      console.error('Stream error:', error);
      setIsStreaming(false);
    }
  }, []);
  
  const resumeWithDecision = useCallback(async (
    decision: HITLDecision,
    threadId: string
  ) => {
    // Send decision to resume endpoint
    const response = await fetch('/api/v1/chat/resume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        threadId,
        userId: getCurrentUserId(),
        decision
      })
    });
    
    // Resume streaming
    // Implementation similar to streamMessage
  }, []);
  
  return {
    messages,
    isStreaming,
    interrupt,
    streamMessage,
    resumeWithDecision
  };
}
```

### Frontend Usage

```tsx
// frontend/app/chat/page.tsx
export default function ChatPage() {
  const { 
    messages, 
    isStreaming, 
    interrupt, 
    streamMessage, 
    resumeWithDecision 
  } = useChatStream();
  
  const handleSendMessage = (message: string) => {
    streamMessage(message, currentThreadId);
  };
  
  const handleHITLDecision = (decision: HITLDecision) => {
    resumeWithDecision(decision, currentThreadId);
  };
  
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <CronJobsSidebar />
      
      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatHeader />
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {/* HITL Approval Card */}
          {interrupt && (
            <HITLApprovalCard
              interrupt={interrupt}
              onDecision={handleHITLDecision}
            />
          )}
          
          {/* Loading indicator */}
          {isStreaming && <StreamingIndicator />}
        </div>
        
        <ChatInput 
          onSend={handleSendMessage}
          disabled={isStreaming}
        />
      </div>
    </div>
  );
}
```

---

## Cron Job Management

### APScheduler Setup

```python
# backend/app/services/cron_service.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import uuid

class CronService:
    """
    Manages scheduled monitoring jobs using APScheduler.
    Syncs with Firestore for persistence.
    """
    
    def __init__(self, firestore_client, monitoring_service):
        self.firestore = firestore_client
        self.monitoring_service = monitoring_service
        
        # Configure APScheduler
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
        }
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self.scheduler.start()
    
    async def create_monitoring_job(
        self,
        config_id: str,
        competitor: str,
        aspects: List[str],
        frequency_hours: int,
        user_id: str
    ) -> str:
        """Create and schedule a monitoring job"""
        
        # Generate job ID
        job_id = f"monitor_{uuid.uuid4().hex[:8]}"
        
        # Add to APScheduler
        self.scheduler.add_job(
            func=self._execute_monitoring_task,
            trigger=IntervalTrigger(hours=frequency_hours),
            id=job_id,
            args=[config_id, competitor, aspects, user_id],
            replace_existing=True,
            next_run_time=datetime.utcnow() + timedelta(seconds=10)  # First run soon
        )
        
        # Save to Firestore
        await self.firestore.collection('cron_jobs').document(job_id).set({
            'config_id': config_id,
            'apscheduler_id': job_id,
            'status': 'running',
            'created_at': firestore.SERVER_TIMESTAMP,
            'next_run': datetime.utcnow() + timedelta(hours=frequency_hours),
            'error_count': 0
        })
        
        # Update config with job ID
        await self.firestore.collection('monitoring_configs').document(
            config_id
        ).update({
            'apscheduler_job_id': job_id,
            'status': 'active'
        })
        
        return job_id
    
    async def _execute_monitoring_task(
        self,
        config_id: str,
        competitor: str,
        aspects: List[str],
        user_id: str
    ):
        """Execute monitoring task (called by APScheduler)"""
        try:
            # Execute monitoring using agent
            results = await self.monitoring_service.execute_monitoring(
                competitor=competitor,
                aspects=aspects,
                user_id=user_id
            )
            
            # Save results
            result_id = uuid.uuid4().hex
            await self.firestore.collection('monitoring_results').document(
                result_id
            ).set({
                'config_id': config_id,
                'competitor': competitor,
                'execution_time': firestore.SERVER_TIMESTAMP,
                'findings': results['findings'],
                'is_significant': results['is_significant'],
                'significance_score': results['significance_score'],
                'notification_sent': False
            })
            
            # Send notification if significant
            if results['is_significant']:
                await self._send_notification(
                    user_id=user_id,
                    competitor=competitor,
                    findings=results['findings']
                )
                
                # Update notification status
                await self.firestore.collection('monitoring_results').document(
                    result_id
                ).update({'notification_sent': True})
            
            # Reset error count
            await self.firestore.collection('cron_jobs').document(
                self.scheduler.get_job(config_id).id
            ).update({'error_count': 0})
        
        except Exception as e:
            # Handle error
            logger.error(f"Monitoring task failed: {e}")
            
            # Increment error count
            job_doc = await self.firestore.collection('cron_jobs').document(
                config_id
            ).get()
            error_count = job_doc.to_dict().get('error_count', 0) + 1
            
            await self.firestore.collection('cron_jobs').document(
                config_id
            ).update({
                'error_count': error_count,
                'last_error': str(e),
                'status': 'failed' if error_count >= 3 else 'running'
            })
    
    async def pause_job(self, job_id: str):
        """Pause a monitoring job"""
        self.scheduler.pause_job(job_id)
        await self.firestore.collection('cron_jobs').document(job_id).update({
            'status': 'paused'
        })
    
    async def resume_job(self, job_id: str):
        """Resume a paused job"""
        self.scheduler.resume_job(job_id)
        await self.firestore.collection('cron_jobs').document(job_id).update({
            'status': 'running'
        })
    
    async def delete_job(self, job_id: str):
        """Delete a monitoring job"""
        self.scheduler.remove_job(job_id)
        await self.firestore.collection('cron_jobs').document(job_id).delete()
        
        # Update config status
        config = await self._find_config_by_job_id(job_id)
        if config:
            await self.firestore.collection('monitoring_configs').document(
                config['id']
            ).update({'status': 'deleted'})
    
    async def load_jobs_on_startup(self):
        """
        Load active jobs from Firestore on server startup.
        Recreate APScheduler jobs.
        """
        jobs = await self.firestore.collection('cron_jobs').where(
            'status', '==', 'running'
        ).get()
        
        for job_doc in jobs:
            job_data = job_doc.to_dict()
            config = await self.firestore.collection('monitoring_configs').document(
                job_data['config_id']
            ).get()
            config_data = config.to_dict()
            
            # Recreate job
            await self.create_monitoring_job(
                config_id=job_data['config_id'],
                competitor=config_data['competitor'],
                aspects=config_data['aspects'],
                frequency_hours=config_data['frequency_hours'],
                user_id=config_data['user_id']
            )
```

### Monitoring Execution Service

```python
# backend/app/services/monitoring_service.py
from .competitor_agent import create_competitor_monitoring_agent

class MonitoringService:
    """
    Executes monitoring tasks using the competitor agent.
    Called by CronService.
    """
    
    def __init__(self, skill_loader, firestore_client):
        self.skill_loader = skill_loader
        self.firestore = firestore_client
    
    async def execute_monitoring(
        self,
        competitor: str,
        aspects: List[str],
        user_id: str
    ) -> dict:
        """
        Execute a monitoring task using the competitor agent.
        
        Unlike interactive chat, this runs:
        - Without streaming
        - Without HITL (approved already)
        - Returns structured results
        """
        
        # Create agent (without HITL middleware for execution)
        agent = create_competitor_monitoring_agent(
            firestore_client=self.firestore,
            skill_loader=self.skill_loader,
            enable_hitl=False  # No approval needed for scheduled runs
        )
        
        # Execute monitoring
        result = await agent.ainvoke({
            "messages": [{
                "role": "system",
                "content": f"""Execute monitoring task for {competitor}.
                Aspects to monitor: {', '.join(aspects)}.
                This is a scheduled execution - provide structured results only.
                """
            }]
        })
        
        # Extract findings
        findings = result.get('findings', {})
        
        # Analyze significance
        significance_analysis = await self._analyze_significance(findings)
        
        return {
            'findings': findings,
            'is_significant': significance_analysis['is_significant'],
            'significance_score': significance_analysis['score'],
            'summary': significance_analysis['summary']
        }
    
    async def _analyze_significance(self, findings: dict) -> dict:
        """
        Analyze if findings are significant.
        Uses rules from competitor_analysis skill.
        """
        skill_content = self.skill_loader.load_full_skill("competitor_analysis")
        
        # Apply significance detection rules
        # Example rules:
        # - New product launch: HIGH significance
        # - Price change > 10%: HIGH significance
        # - Social sentiment shift: MEDIUM significance
        # - Minor news mention: LOW significance
        
        # ... implementation
        pass
```

### Cron Jobs API

```python
# backend/app/api/v1/crons.py
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix="/crons", tags=["crons"])

@router.get("/")
async def list_cron_jobs(
    user_id: str = Depends(get_current_user_id)
) -> List[CronJob]:
    """List all cron jobs for current user"""
    configs = await firestore.collection('monitoring_configs').where(
        'user_id', '==', user_id
    ).where(
        'status', 'in', ['active', 'paused']
    ).get()
    
    jobs = []
    for config_doc in configs:
        config_data = config_doc.to_dict()
        job_data = await firestore.collection('cron_jobs').document(
            config_data['apscheduler_job_id']
        ).get()
        
        jobs.append({
            **config_data,
            'job_status': job_data.to_dict()
        })
    
    return jobs

@router.post("/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause a cron job"""
    await cron_service.pause_job(job_id)
    return {"status": "paused"}

@router.post("/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume a paused job"""
    await cron_service.resume_job(job_id)
    return {"status": "running"}

@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a cron job"""
    await cron_service.delete_job(job_id)
    return {"status": "deleted"}

@router.get("/{job_id}/results")
async def get_job_results(
    job_id: str,
    limit: int = 50
) -> List[MonitoringResult]:
    """Get recent results for a job"""
    config = await firestore.collection('monitoring_configs').document(
        job_id
    ).get()
    config_id = config.id
    
    results = await firestore.collection('monitoring_results').where(
        'config_id', '==', config_id
    ).order_by('execution_time', direction='DESCENDING').limit(limit).get()
    
    return [doc.to_dict() for doc in results]
```

### Frontend Cron Sidebar

```tsx
// frontend/components/chat/cron-sidebar.tsx
export function CronJobsSidebar() {
  const { data: jobs, isLoading } = useQuery({
    queryKey: ['cron-jobs'],
    queryFn: () => fetch('/api/v1/crons').then(r => r.json())
  });
  
  const pauseMutation = useMutation({
    mutationFn: (jobId: string) => 
      fetch(`/api/v1/crons/${jobId}/pause`, { method: 'POST' })
  });
  
  const deleteMutation = useMutation({
    mutationFn: (jobId: string) =>
      fetch(`/api/v1/crons/${jobId}`, { method: 'DELETE' })
  });
  
  return (
    <div className="w-80 border-r border-gray-800 bg-gray-900">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Monitoring Jobs
        </h2>
      </div>
      
      <ScrollArea className="h-[calc(100vh-80px)]">
        <div className="p-4 space-y-3">
          {isLoading ? (
            <div className="text-center text-gray-500">Loading...</div>
          ) : jobs.length === 0 ? (
            <div className="text-center text-gray-500">
              No monitoring jobs yet
            </div>
          ) : (
            jobs.map(job => (
              <Card key={job.id} className="p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-semibold">{job.competitor}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      Every {job.frequency_hours}h
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => pauseMutation.mutate(job.id)}>
                        <Pause className="w-4 h-4 mr-2" />
                        {job.status === 'paused' ? 'Resume' : 'Pause'}
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => /* view results */}>
                        <BarChart className="w-4 h-4 mr-2" />
                        View Results
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        className="text-red-500"
                        onClick={() => deleteMutation.mutate(job.id)}
                      >
                        <Trash className="w-4 h-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                
                <div className="mt-2 flex flex-wrap gap-1">
                  {job.aspects.map(aspect => (
                    <Badge key={aspect} variant="outline" className="text-xs">
                      {aspect}
                    </Badge>
                  ))}
                </div>
                
                <div className="mt-2 text-xs text-gray-500">
                  Next run: {formatRelativeTime(job.next_run)}
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
```

---

## GenUI Response Formatting

### What is GenUI?

**Generative UI** = LLM generates structured UI components, not just text.

Example: Instead of "Nike launched a new shoe", agent returns:

```json
{
  "type": "card",
  "title": "Product Launch Detected",
  "data": {
    "competitor": "Nike",
    "product": "Air Max 2026",
    "launch_date": "2026-02-10",
    "price": "$180",
    "significance": "high"
  }
}
```

### GenUI Middleware

```python
# backend/app/middleware/genui_middleware.py
from langchain.agents.middleware import AgentMiddleware
from typing import Any, Dict

class GenUIMiddleware(AgentMiddleware):
    """
    Converts structured agent outputs to UI components.
    Streams components via 'custom' mode.
    """
    
    def after_model(
        self, 
        state: dict, 
        runtime
    ) -> Optional[Dict[str, Any]]:
        """
        Convert structured outputs to GenUI components.
        """
        # Check if response contains structured data
        last_message = state.get('messages', [])[-1]
        
        if hasattr(last_message, 'structured_response'):
            # Convert to UI component
            component = self._create_component(
                last_message.structured_response
            )
            
            # Stream via custom mode
            runtime.stream_custom(component)
        
        return None
    
    def _create_component(self, data: dict) -> dict:
        """
        Convert structured data to UI component schema.
        """
        # Determine component type
        if 'findings' in data:
            return {
                'type': 'monitoring_results_table',
                'data': self._format_monitoring_table(data['findings'])
            }
        
        elif 'timeline' in data:
            return {
                'type': 'timeline',
                'data': self._format_timeline(data['timeline'])
            }
        
        elif 'comparison' in data:
            return {
                'type': 'comparison_card',
                'data': self._format_comparison(data['comparison'])
            }
        
        return {'type': 'text', 'data': data}
    
    def _format_monitoring_table(self, findings: dict) -> dict:
        return {
            'title': f"Monitoring Results - {findings['competitor']}",
            'columns': ['Date', 'Category', 'Finding', 'Significance'],
            'rows': [
                {
                    'date': f['timestamp'],
                    'category': f['aspect'],
                    'finding': f['summary'],
                    'significance': f['significance']
                }
                for f in findings.get('items', [])
            ]
        }
```

### Frontend GenUI Renderer

```tsx
// frontend/components/chat/genui-renderer.tsx
interface GenUIComponent {
  type: string;
  data: any;
}

export function GenUIRenderer({ component }: { component: GenUIComponent }) {
  switch (component.type) {
    case 'monitoring_results_table':
      return <MonitoringResultsTable data={component.data} />;
    
    case 'timeline':
      return <TimelineView data={component.data} />;
    
    case 'comparison_card':
      return <ComparisonCard data={component.data} />;
    
    case 'card':
      return <InfoCard data={component.data} />;
    
    default:
      return <div>Unknown component: {component.type}</div>;
  }
}

function MonitoringResultsTable({ data }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{data.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              {data.columns.map(col => (
                <TableHead key={col}>{col}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.rows.map((row, i) => (
              <TableRow key={i}>
                <TableCell>{row.date}</TableCell>
                <TableCell>{row.category}</TableCell>
                <TableCell>{row.finding}</TableCell>
                <TableCell>
                  <Badge variant={
                    row.significance === 'high' ? 'destructive' :
                    row.significance === 'medium' ? 'default' :
                    'secondary'
                  }>
                    {row.significance}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function TimelineView({ data }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.events.map((event, i) => (
            <div key={i} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                {i < data.events.length - 1 && (
                  <div className="w-0.5 h-full bg-blue-500/30" />
                )}
              </div>
              <div className="flex-1 pb-4">
                <div className="text-sm text-gray-400">{event.date}</div>
                <div className="font-semibold">{event.title}</div>
                <div className="text-sm text-gray-300">{event.description}</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Basic agent setup without advanced features

**Tasks**:
1. ✅ Install dependencies
   ```bash
   # Backend
   pip install langchain langchain-google-genai langgraph tavily-python apscheduler
   
   # Frontend
   cd frontend && pnpm add @langchain/langgraph-sdk
   ```

2. ✅ Create agent skills structure
   - Set up `backend/app/agents/skills/` directory
   - Create first skill: `competitor_search`
   - Implement `SkillLoader` class

3. ✅ Implement Orchestrator Agent
   - Simple routing with structured output
   - Test routing to different agents

4. ✅ Implement Competitor Monitoring Agent (Basic)
   - Without HITL (just approve all)
   - Without GenUI (text only)
   - Basic Tavily search integration

5. ✅ Setup Memory System
   - InMemorySaver for checkpoints
   - Firestore collections created
   - Basic FirestoreMemoryMiddleware

**Deliverable**: Chat works, agent can search competitors, no approval flow yet

---

### Phase 2: HITL & Streaming (Week 2)
**Goal**: Add approval flow and real-time streaming

**Tasks**:
1. ✅ Implement HITL Middleware
   - Add `HumanInTheLoopMiddleware` to agent
   - Configure `interrupt_on` for monitoring config

2. ✅ Implement SSE Streaming
   - Create `/api/v1/chat/stream` endpoint
   - Stream tokens, updates, interrupts
   - Frontend `useChatStream` hook

3. ✅ Build HITL UI Components
   - `HITLApprovalCard` component
   - Approve/Edit/Reject functionality
   - Show monitoring configuration details

4. ✅ Implement Resume Endpoint
   - `/api/v1/chat/resume` endpoint
   - Handle user decisions
   - Resume agent execution

**Deliverable**: Chat with streaming, user can approve monitoring jobs

---

### Phase 3: Cron Jobs & Execution (Week 3)
**Goal**: Scheduled monitoring execution

**Tasks**:
1. ✅ Setup APScheduler
   - Configure `CronService`
   - Persist jobs to SQLite
   - Sync with Firestore

2. ✅ Implement Monitoring Execution
   - `MonitoringService` for scheduled runs
   - Execute agent without HITL
   - Save results to Firestore

3. ✅ Build Significance Detection
   - Implement `analyze_significance` skill
   - Define significance rules
   - Calculate significance scores

4. ✅ Implement Notifications
   - Gmail API integration
   - Email templates
   - Notification logic (only if significant)

5. ✅ Build Cron Management UI
   - `CronJobsSidebar` component
   - List/Pause/Resume/Delete jobs
   - View job results

**Deliverable**: Fully functional scheduled monitoring

---

### Phase 4: GenUI & Polish (Week 4)
**Goal**: Rich UI components and production-ready

**Tasks**:
1. ✅ Implement GenUI Middleware
   - Convert structured outputs to components
   - Stream via `custom` mode

2. ✅ Build GenUI Components
   - `MonitoringResultsTable`
   - `TimelineView`
   - `ComparisonCard`
   - `InfoCard`

3. ✅ Add Error Handling
   - Retry logic for failed jobs
   - Error notifications
   - Graceful degradation

4. ✅ Performance Optimization
   - Caching for Firestore queries
   - Rate limiting for API calls
   - Optimize token usage

5. ✅ Testing & Documentation
   - Unit tests for agents
   - Integration tests for cron jobs
   - API documentation

**Deliverable**: Production-ready system with rich UI

---

## Technical Stack

### Backend
- **Python 3.11+**
- **FastAPI** (REST API + SSE)
- **LangChain 1.0** (Agent framework)
- **LangGraph** (Under the hood, via LangChain)
- **Google Gemini** (gemini-2.0-flash-exp)
- **Tavily** (Search API)
- **APScheduler** (Cron jobs)
- **Firebase/Firestore** (Persistence)
- **Gmail API** (Notifications)

### Frontend
- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui** (UI components)
- **TanStack Query** (Data fetching)
- **EventSource** (SSE client)

### Infrastructure
- **Firestore** (Database)
- **Cloud Run** (Deployment)
- **Cloud Scheduler** (Backup for cron)

---

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator_agent.py         # Routes to specialized agents
│   │   ├── competitor_monitoring_agent.py # Main monitoring agent
│   │   │
│   │   ├── skills/                       # Agent Skills (progressive disclosure)
│   │   │   ├── __init__.py
│   │   │   ├── skill_loader.py           # Load skills on demand
│   │   │   │
│   │   │   ├── competitor_search/
│   │   │   │   ├── SKILL.md              # Search skill instructions
│   │   │   │   ├── search_strategies.md
│   │   │   │   └── examples/
│   │   │   │
│   │   │   ├── competitor_analysis/
│   │   │   │   ├── SKILL.md
│   │   │   │   ├── analysis_frameworks.md
│   │   │   │   └── significance_detection.md
│   │   │   │
│   │   │   └── notification_management/
│   │   │       ├── SKILL.md
│   │   │       ├── email_templates/
│   │   │       └── notification_rules.md
│   │   │
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── search_tools.py           # Tavily + Google Grounding
│   │       ├── monitoring_tools.py       # Monitoring config creation
│   │       └── notification_tools.py     # Gmail API
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── firestore_memory_middleware.py # Cross-thread memory
│   │   ├── genui_middleware.py           # Format responses as UI components
│   │   └── logging_middleware.py         # Request logging
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cron_service.py               # APScheduler management
│   │   ├── monitoring_service.py         # Execute monitoring tasks
│   │   ├── notification_service.py       # Send notifications
│   │   └── memory_service.py             # Memory management
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py                       # Chat request/response models
│   │   ├── monitoring.py                 # Monitoring config models
│   │   ├── genui.py                      # UI component schemas
│   │   └── cron.py                       # Cron job models
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── chat.py                   # /chat/stream, /chat/resume
│   │       ├── crons.py                  # /crons CRUD endpoints
│   │       └── monitoring.py             # /monitoring endpoints
│   │
│   └── core/
│       ├── __init__.py
│       ├── config.py                     # Settings
│       ├── firebase.py                   # Firestore client
│       └── memory.py                     # HybridMemoryManager
│
├── jobs.db                               # APScheduler SQLite
├── requirements.txt
└── pyproject.toml

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx                      # Main chat page
│   ├── cron-jobs/
│   │   └── page.tsx                      # Standalone cron management
│   └── layout.tsx
│
├── components/
│   ├── chat/
│   │   ├── chat-area.tsx
│   │   ├── chat-header.tsx
│   │   ├── chat-input.tsx
│   │   ├── message-bubble.tsx
│   │   ├── hitl-approval-card.tsx        # HITL UI
│   │   ├── cron-sidebar.tsx              # Cron jobs sidebar
│   │   └── genui-renderer.tsx            # Render UI components
│   │
│   └── genui/
│       ├── monitoring-results-table.tsx
│       ├── timeline-view.tsx
│       ├── comparison-card.tsx
│       └── info-card.tsx
│
├── hooks/
│   ├── use-chat-stream.ts                # SSE streaming hook
│   └── use-cron-jobs.ts                  # Cron management hook
│
└── lib/
    ├── api.ts                            # API client
    └── types.ts                          # TypeScript types
```

---

## Summary & Recommendations

### Key Decisions Made:

1. **Agent Skills**: Use Anthropic's specification with progressive disclosure
   - Skills are folders with SKILL.md files
   - Agent reads frontmatter first, loads full content when needed
   - More token-efficient than loading everything

2. **Memory**: Hybrid approach (InMemorySaver + Firestore)
   - InMemorySaver: Thread-level checkpoints (LangChain built-in)
   - Firestore: Cross-thread memory, job configs, results
   - Best of both worlds: Performance + Persistence

3. **Streaming**: SSE (Server-Sent Events)
   - Simpler than WebSocket
   - Built-in browser support
   - Perfect for one-way streaming
   - Use `stream_mode=["messages", "updates", "custom"]`

4. **HITL**: LangChain's built-in middleware
   - `HumanInTheLoopMiddleware` with `interrupt_on`
   - Detect interrupts in SSE stream
   - Resume with `Command(resume={decision})`

5. **Cron Jobs**: APScheduler
   - Lightweight, dynamic job scheduling
   - Persist to SQLite + sync with Firestore
   - Load jobs on startup

### Next Steps:

1. **Review this plan** - Confirm approach makes sense
2. **Phase 1 Implementation** - Start with foundation
3. **Iterative Development** - Build phase by phase
4. **Testing** - Test after each phase

### Questions for You:

1. Does this architecture align with your vision?
2. Any concerns about the tech stack choices?
3. Should we start with Phase 1, or do you want modifications first?
4. Any specific requirements I missed?

Let me know your thoughts and we can proceed! 🚀
