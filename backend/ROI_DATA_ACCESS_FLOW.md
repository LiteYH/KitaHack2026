# ROI Data Access Flow with Human-in-the-Loop (HITL)

## Overview

This document explains how the chatbot orchestrator handles ROI-related queries with automatic user approval (Human-in-the-Loop pattern) and Gmail-authenticated data access.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ROI QUERY FLOW                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│  User Types  │    "What was my ROI for the last 7 days?"
│   Message    │
└──────┬───────┘
       │
       │ 1. Frontend retrieves user Gmail from Firebase Auth
       │
       v
┌──────────────────────┐
│  Frontend            │
│  (chat-area.tsx)     │
│                      │
│  • Get user email    │──→  const userEmail = user?.email
│  • Pass to backend   │──→  user_email: userEmail
└──────┬───────────────┘
       │
       │ 2. Send request with user_email
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  Backend API                                                               │
│  (routers/chat.py)                                                        │
│                                                                            │
│  POST /api/v1/chat/message                                                │
│    {                                                                       │
│      "message": "What was my ROI for the last 7 days?",                  │
│      "user_email": "user@gmail.com",  ← User's Gmail                     │
│      "conversation_history": [...],                                       │
│      "thread_id": "abc-123"                                               │
│    }                                                                       │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 3. Call LangGraph Agent Service
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  LangGraph Agent Service                                                   │
│  (services/agent_service.py)                                              │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │  System Message (with user email context)               │            │
│  │  ────────────────────────────────────────────────────── │            │
│  │  "You are BossolutionAI...                              │            │
│  │                                                           │            │
│  │  🔑 AUTHENTICATED USER CONTEXT:                          │            │
│  │  User Gmail: user@gmail.com                             │            │
│  │                                                           │            │
│  │  When using roi_analysis tool, pass:                    │            │
│  │    user_email='user@gmail.com'"                         │            │
│  └─────────────────────────────────────────────────────────┘            │
│                                                                            │
│  4. Agent detects ROI query and decides to use roi_analysis tool         │
│                                                                            │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 5. LangGraph HITL Middleware intercepts
       │    (interrupt_before=["tools"])
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  LangGraph HITL Pause                                                      │
│  ────────────────────────────────────────────────────────────────────── │
│                                                                            │
│  • Agent execution PAUSED                                                 │
│  • Tool call intercepted BEFORE execution                                │
│  • State saved with thread_id                                            │
│  • Approval request created                                               │
│                                                                            │
│  Approval Request:                                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │ 🔒 ROI Data Access Request                                  │         │
│  │                                                              │         │
│  │ I need your permission to access your ROI data...          │         │
│  │                                                              │         │
│  │ 📊 What I'll Access:                                        │         │
│  │ - Video performance metrics                                 │         │
│  │ - Revenue and cost data                                     │         │
│  │ - ROI calculations                                          │         │
│  │                                                              │         │
│  │ 🔐 Your Account:                                            │         │
│  │ - Gmail: user@gmail.com                                     │         │
│  │ - Filter: user_email == 'user@gmail.com'                   │         │
│  │                                                              │         │
│  │ 🛡️ Privacy Guarantees:                                      │         │
│  │ ✅ Only YOUR data (filtered by Gmail)                       │         │
│  │ ✅ Session-only usage                                        │         │
│  │ ✅ No storage or sharing                                     │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                            │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 6. Return approval request to frontend
       │
       v
┌──────────────────────┐
│  Frontend            │
│                      │
│  • Show approval UI  │
│  • [Yes] [No] buttons│
└──────┬───────────────┘
       │
       │ 7. User clicks "Yes" (approved)
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  Backend receives approval                                                 │
│  {                                                                         │
│    "approval_decision": {                                                  │
│      "approved": true,                                                     │
│      "thread_id": "abc-123",                                              │
│      "tool_name": "roi_analysis"                                          │
│    }                                                                       │
│  }                                                                         │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 8. Resume LangGraph execution from saved state
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  ROI Analysis Tool Execution                                               │
│  (services/roi_tool.py)                                                   │
│                                                                            │
│  def _arun(user_message, user_email):                                     │
│      # Now executes because user approved                                 │
│                                                                            │
│      print("🎯 Executing ROI Analysis (Post-Approval)")                   │
│      print(f"  ✓ User email: {user_email}")                              │
│      print(f"  ✓ Approval: GRANTED")                                      │
│                                                                            │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 9. Call ROI Analysis Service
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  ROI Analysis Service                                                      │
│  (services/roi_analysis_service.py)                                       │
│                                                                            │
│  async def analyze_query(user_message, user_email):                       │
│      # Step 1: Query Firebase                                             │
│      query = db.collection('ROI')                                         │
│               .where('user_email', '==', user_email)  ← Gmail filter     │
│                                                                            │
│      videos = query.stream()                                              │
│                                                                            │
│      # Step 2: Analyze data                                               │
│      metrics = calculate_metrics(videos)                                  │
│                                                                            │
│      # Step 3: Generate AI insights                                       │
│      insights = model.invoke(analyze_prompt + metrics)                    │
│                                                                            │
│      # Step 4: Create chart configurations                                │
│      charts = generate_charts(videos, metrics)                            │
│                                                                            │
│      return {                                                              │
│        "analysis": insights,                                               │
│        "charts": charts,                                                   │
│        "success": True                                                     │
│      }                                                                     │
│                                                                            │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 10. Return analysis result
       │
       v
┌──────────────────────────────────────────────────────────────────────────┐
│  Frontend receives response                                                │
│  {                                                                         │
│    "message": "## Your ROI Performance (Last 7 Days)\n...",              │
│    "charts": [                                                             │
│      {                                                                     │
│        "type": "line",                                                     │
│        "title": "ROI Trend",                                              │
│        "data": {...}                                                       │
│      }                                                                     │
│    ],                                                                      │
│    "requires_approval": false                                             │
│  }                                                                         │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
       │ 11. Render response with charts
       │
       v
┌──────────────────────┐
│  User sees:          │
│                      │
│  📊 Your ROI Report  │
│  ├─ AI Analysis      │
│  ├─ Chart 1          │
│  ├─ Chart 2          │
│  └─ Recommendations  │
└──────────────────────┘
```

## Key Components

### 1. Frontend (chat-area.tsx)

**Responsibility:** Retrieve authenticated user's Gmail and pass to backend

```typescript
// Get user email from Firebase Auth context
const userEmail = user?.email
const userId = user?.uid

// Send to backend
const response = await sendChatMessage({
  message: text,
  user_email: userEmail,  // ← Key: Gmail passed here
  // ...
})
```

### 2. Agent Service (agent_service.py)

**Responsibility:** Orchestrate LangGraph agent with HITL middleware

```python
# Initialize agent with interrupt_before
self.agent = create_react_agent(
    model=self.model,
    tools=[roi_analysis_tool],
    checkpointer=self.checkpointer,
    interrupt_before=["tools"]  # ← Pauses before tool execution
)

# Add user email to system context
if user_email:
    system_content += f"User Gmail: {user_email}"
```

### 3. ROI Tool (roi_tool.py)

**Responsibility:** Execute ROI analysis after approval

```python
class ROIAnalysisTool(BaseTool):
    name = "roi_analysis"
    
    async def _arun(self, user_message: str, user_email: str):
        # This only runs AFTER user approves
        result = await roi_analysis_service.analyze_query(
            user_message=user_message,
            user_email=user_email  # ← Used to filter Firebase
        )
        return json.dumps(result)
```

### 4. ROI Analysis Service (roi_analysis_service.py)

**Responsibility:** Query Firebase and analyze data

```python
async def fetch_user_roi_data(self, user_email: str, days: Optional[int]):
    # Query Firebase with user_email filter
    query = self.db.collection('ROI').where('user_email', '==', user_email)
    docs = query.stream()
    
    videos = [doc.to_dict() for doc in docs]
    return videos
```

## Security Features

### 1. **Authentication Required**
- User must be logged in via Firebase Auth
- Gmail is retrieved from auth context
- No anonymous access to ROI data

### 2. **Human-in-the-Loop Approval**
- LangGraph pauses before accessing Firebase
- User sees explicit approval dialog
- Explains what data will be accessed
- User can approve or deny

### 3. **Data Isolation**
- Firebase queries filter by `user_email == user@gmail.com`
- Users only see their own data
- No cross-user data leakage possible

### 4. **Session-Only Access**
- Data retrieved only during active session
- No caching or persistent storage
- Data discarded after analysis

### 5. **Transparency**
- Approval dialog shows exactly what data is accessed
- Shows user's Gmail being used for filtering
- Explains privacy guarantees

## Example Queries

The system automatically detects ROI-related queries:

**Financial Metrics:**
- "What is my ROI for the last 7 days?"
- "Show me my revenue breakdown"
- "How much profit did I make last month?"
- "Compare my costs vs revenue"

**Video Performance:**
- "Which video performed best?"
- "Show me my top 5 videos by engagement"
- "What's my average retention rate?"
- "Analyze my video metrics"

**Time-Based:**
- "ROI trends for the past 30 days"
- "Performance this week"
- "Compare last month to this month"

## Error Handling

### No User Email
If user is not logged in:
```json
{
  "success": false,
  "error": "User email is required",
  "analysis": "⚠️ Authentication Required\n\nPlease log in to access your ROI data..."
}
```

### User Denies Approval
If user clicks "No":
```
"I understand. I won't access your ROI data. 
Feel free to ask me anything else about marketing strategies!"
```

### No Data Found
If user has no ROI data:
```json
{
  "found_data": false,
  "message": "No ROI data found for the specified period.",
  "analysis": "I couldn't find any ROI data..."
}
```

## Testing

### Test 1: ROI Query Detection
```
User: "What was my ROI last week?"
Expected: Approval dialog appears
```

### Test 2: Email Passing
```
Check logs:
📧 [AUTH] User Gmail retrieved: user@gmail.com
✓ User email: user@gmail.com
✓ Filter: user_email == 'user@gmail.com'
```

### Test 3: Approval Flow
```
1. User asks ROI question
2. See approval dialog
3. Click "Yes"
4. See ROI analysis with charts
```

### Test 4: Denial Flow
```
1. User asks ROI question
2. See approval dialog
3. Click "No"
4. See supportive message (no data access)
```

## Firebase Data Structure

```json
{
  "ROI": {
    "video_id_1": {
      "user_email": "user@gmail.com",  ← Filter field
      "title": "My Video Title",
      "publish_date": "2026-02-14T10:00:00Z",
      "metrics": {
        "views": 10000,
        "likes": 500,
        "comments": 50,
        "retention_rate_percent": 45.2
      },
      "revenue": {
        "total_revenue_usd": 250.50,
        "ad_revenue_usd": 200.00,
        "sponsorship_revenue_usd": 50.50
      },
      "costs": {
        "total_cost_usd": 100.00,
        "production_cost_usd": 80.00,
        "promotion_cost_usd": 20.00
      },
      "roi_analysis": {
        "roi_percent": 150.5,
        "profit_usd": 150.50
      }
    }
  }
}
```

## Conclusion

This implementation provides:
- ✅ Automatic ROI query detection
- ✅ Secure Gmail-based authentication
- ✅ Human-in-the-Loop approval flow
- ✅ Privacy-preserving data access (user_email filtering)
- ✅ Comprehensive error handling
- ✅ Transparent data access explanation
- ✅ Professional user experience

The system ensures users always have control over their data access while providing a seamless AI-powered analytics experience.
