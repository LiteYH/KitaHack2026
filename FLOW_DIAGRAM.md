# 🔄 Campaign Orchestrator Flow Diagram

## System Flow: User Query to AI Response

```
┌─────────────────────────────────────────────────────────────────────┐
│                         1. USER QUERY                               │
│   "How can I optimize my current ongoing campaigns?"                │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    2. FRONTEND (chat-area.tsx)                      │
│                                                                      │
│   • User types message in chat UI                                   │
│   • Calls streamChatMessage() with userId                           │
│   • Sends to: POST /api/v1/chat/stream                              │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    3. API ROUTER (chat.py)                          │
│                                                                      │
│   • Receives ChatRequest { message, user_id, history }              │
│   • Routes to chat_service.chat_stream()                            │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  4. CHAT SERVICE (chat_service.py)                  │
│                                                                      │
│   • Calls orchestrator_service.orchestrate_response()               │
│   • Receives enriched prompt + campaign context                     │
│   • Sends to Gemini AI                                              │
│   • Streams response back                                           │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              5. ORCHESTRATOR (orchestrator_service.py)              │
│                                                                      │
│   ┌──────────────────────────────────────────────────────┐          │
│   │ 5a. ANALYZE INTENT                                   │          │
│   │                                                      │          │
│   │ • Detect keywords: "optimize", "current", "ongoing"  │          │
│   │                                                      │          │
│   │ Result:                                              │          │
│   │   needs_campaign_data: True                          │          │
│   │   status_filter: "ongoing"                           │          │
│   │   intent_type: "optimization"                        │          │
│   └───────────────────┬──────────────────────────────────┘          │
│                       │                                              │
│                       ▼                                              │
│   ┌──────────────────────────────────────────────────────┐          │
│   │ 5b. GET RELEVANT CAMPAIGNS                           │          │
│   │                                                      │          │
│   │ • Calls campaign_service.get_campaigns_with_metrics()│          │
│   │ • Filters: userID + status="ongoing"                 │          │
│   └───────────────────┬──────────────────────────────────┘          │
│                       │                                              │
│                       ▼                                              │
│   ┌──────────────────────────────────────────────────────┐          │
│   │ 5c. BUILD ENRICHED PROMPT                            │          │
│   │                                                      │          │
│   │ Original: 48 chars                                   │          │
│   │ "How can I optimize my current ongoing campaigns?"   │          │
│   │                                                      │          │
│   │ Enriched: 1,775 chars                                │          │
│   │ • Summary: 7 campaigns, $53k budget, ROAS 6.8x      │          │
│   │ • Details: Each campaign with full metrics           │          │
│   │ • Instructions: Provide optimization recommendations │          │
│   └───────────────────┬──────────────────────────────────┘          │
│                       │                                              │
└───────────────────────┼──────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              6. CAMPAIGN SERVICE (campaign_service.py)              │
│                                                                      │
│   ┌──────────────────────────────────────────────────────┐          │
│   │ 6a. FETCH FROM FIRESTORE                             │          │
│   │                                                      │          │
│   │   db.collection('campaign_details')                  │          │
│   │     .where('userID', '==', user_id)                  │          │
│   │     .where('status', '==', 'ongoing')                │          │
│   │     .stream()                                        │          │
│   │                                                      │          │
│   │   Returns: 7 campaigns                               │          │
│   └───────────────────┬──────────────────────────────────┘          │
│                       │                                              │
│                       ▼                                              │
│   ┌──────────────────────────────────────────────────────┐          │
│   │ 6b. CALCULATE METRICS                                │          │
│   │                                                      │          │
│   │   For each campaign:                                 │          │
│   │   • CTR = clicks / impressions * 100                 │          │
│   │   • CVR = purchases / clicks * 100                   │          │
│   │   • ROAS = conversionValue / amountSpent             │          │
│   │   • Budget Utilization = amountSpent / totalBudget   │          │
│   │   • Cost per Click = amountSpent / clicks            │          │
│   │   • Cost per Conversion = amountSpent / purchases    │          │
│   └───────────────────┬──────────────────────────────────┘          │
│                       │                                              │
│                       ▼                                              │
│   ┌──────────────────────────────────────────────────────┐          │
│   │ 6c. GENERATE SUMMARY                                 │          │
│   │                                                      │          │
│   │   Aggregate across all campaigns:                    │          │
│   │   • Total budget: $53,000                            │          │
│   │   • Total spent: $33,500                             │          │
│   │   • Overall ROAS: 6.8x                               │          │
│   │   • Overall CTR: 5.2%                                │          │
│   │   • Average metrics                                  │          │
│   └───────────────────────────────────────────────────────          │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     7. GEMINI AI (Google)                           │
│                                                                      │
│   Receives: Enriched prompt with:                                   │
│   • User's question                                                 │
│   • All campaign data                                               │
│   • Performance metrics                                             │
│   • Specific instructions                                           │
│                                                                      │
│   Generates: Personalized recommendations based on actual data      │
│                                                                      │
│   Example Output:                                                   │
│   "Based on your 7 ongoing campaigns with $53k total budget:        │
│                                                                      │
│   ## Top Performers                                                 │
│   1. **Influencer KOL Campaign** - ROAS 8.2x, keep this running    │
│   2. **Valentine Couple Outfit** - Strong CVR 2.2%                  │
│                                                                      │
│   ## Needs Optimization                                             │
│   1. **Flash Sale Hoodies** - CTR only 5.7% vs avg 5.2%            │
│      → Recommendation: Test new creative, A/B test CTAs             │
│   2. **Back to Uni** - Budget 61% used but ROAS 5.8x               │
│      → Recommendation: Increase budget for this winner              │
│                                                                      │
│   ## Budget Allocation                                              │
│   • Shift $2k from lower ROAS campaigns to KOL campaign            │
│   • Pause campaigns with ROAS < 4x                                  │
│   ..."                                                              │
└──────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    8. STREAM BACK TO USER                           │
│                                                                      │
│   • Chat service streams response chunks                            │
│   • Router forwards to frontend                                     │
│   • User sees AI typing in real-time                                │
│   • Markdown formatting renders beautifully                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Decision Points

### When Campaign Data Is Fetched

```
User Query
    │
    ├─ Contains campaign keywords? ──────────┐
    │  (campaign, optimize, performance, etc.) │
    │                                          │
    ├─ YES ─────────────────────────┐         │
    │                                │         │
    │  Analyze for filters:          │         │
    │  • Status (ongoing/paused)     │         │
    │  • Platform (Instagram, etc.)  │         │
    │                                │         │
    │  Fetch campaigns ───────────────────────┤
    │  Calculate metrics                      │
    │  Enrich prompt                          │
    │                                          │
    └─ NO ──────────────────────────┐         │
                                     │         │
       Skip campaign fetching        │         │
       Use original query ────────────────────┤
                                              │
                                              ▼
                                    Send to Gemini AI
```

### Filtering Logic

```
Intent Analysis Result
    │
    ├─ status_filter: "ongoing" ──────┐
    │                                  │
    ├─ platform_filter: "Instagram" ───┤
    │                                  │
    └─ user_id: "DT4DNex..." ─────────┤
                                       │
                                       ▼
                        Firestore Query Builder
                                       │
    collection('campaign_details')     │
      .where('userID', '==', user_id) ─┤
      .where('status', '==', 'ongoing')─┤
      .where('platform', '==', 'Instagram')
                                       │
                                       ▼
                              Execute & Return Results
```

---

## Data Flow Example

### Input Query
```
"How can I optimize my current ongoing campaigns?"
```

### Intent Detection
```json
{
  "needs_campaign_data": true,
  "status_filter": "ongoing",
  "platform_filter": null,
  "intent_type": "optimization"
}
```

### Firestore Query
```python
db.collection('campaign_details')
  .where('userID', '==', 'DT4DNex2L1N2rZ9kPddEzqougK22')
  .where('status', '==', 'ongoing')
```

### Retrieved Campaigns (7 results)
```
1. Valentine Couple Outfit Drop - Instagram - ROAS 6.06x
2. Summer Sneakers Launch - Facebook - ROAS 8.25x
3. Back to Uni Streetwear - E-commerce - ROAS 5.77x
4. Influencer KOL Campaign - KOL - ROAS 8.17x
5. Ramadan Modest Collection - Instagram - ROAS 8.0x
6. Flash Sale Hoodies - Facebook - ROAS 5.68x
7. CNY Streetwear Sale - Instagram - ROAS 6.48x
```

### Metrics Calculated
```
Campaign 1: CTR 5.28%, CVR 2.21%, ROAS 6.06x, Cost/Conv $24.76
Campaign 2: CTR 5.83%, CVR 2.29%, ROAS 8.25x, Cost/Conv $20.00
... (for all 7 campaigns)

Summary:
- Total Budget: $53,000
- Total Spent: $33,500
- Overall ROAS: 6.8x
- Overall CTR: 5.2%
```

### Enriched Prompt to AI
```markdown
# CONTEXT: User's Campaign Data
The user has 7 ongoing campaigns...

## Overall Performance Summary:
- Total Budget: $53,000
- Total Spent: $33,500
...

## Individual Campaign Details:
1. Valentine Couple Outfit Drop
   - Status: ONGOING
   - Metrics: CTR 5.28%, CVR 2.21%, ROAS 6.06x
...

# USER'S QUESTION:
How can I optimize my current ongoing campaigns?

# INSTRUCTIONS:
Analyze the campaign performance data above and provide specific,
actionable optimization recommendations...
```

### AI Response
```markdown
Based on your 7 ongoing campaigns with strong overall ROAS of 6.8x,
here are my optimization recommendations:

## 🎯 Top Performers - Scale These
1. **Summer Sneakers Launch** (ROAS: 8.25x)
   - Increase budget by 20%
   - This is your best performer
...
```

---

## Architecture Benefits

✅ **Separation of Concerns**
- Orchestrator: Intent analysis
- Campaign Service: Data operations
- Chat Service: AI communication

✅ **Automatic Context Enhancement**
- No manual data fetching needed
- AI always has full campaign context

✅ **Scalable & Maintainable**
- Easy to add new filters
- Easy to add new metrics
- Easy to add new intents

✅ **Intelligent Query Processing**
- Keyword-based intent detection
- Automatic filter extraction
- Context-aware responses

---

## Summary

The orchestrator acts as an intelligent middleware that:
1. Understands what the user wants
2. Fetches the right data
3. Enriches the AI's context
4. Enables data-driven responses

**Result**: Users get personalized, accurate recommendations based on their actual campaign performance! 🎉
