# 🎯 Quick Reference Card - Campaign Orchestrator

## 🔥 Test Queries (Copy & Paste These)

```
How can I optimize my current ongoing campaigns?
Show me my paused campaigns performance
What's my Instagram campaign doing?
Which campaign should I increase budget for?
How are my Facebook campaigns performing?
Which campaigns have low ROAS?
Show me campaign performance summary
What's my overall ROI?
```

## 📊 Test User ID

```
DT4DNex2L1N2rZ9kPddEzqougK22
```

## ⚡ Quick Commands

### Start Backend
```bash
cd backend
python -m uvicorn main:app --reload
# Backend: http://localhost:8000
```

### Start Frontend
```bash
cd frontend
npm run dev  
# Frontend: http://localhost:3000
```

### Run Tests
```bash
cd backend
python test_orchestrator.py
```

### Seed More Campaigns
```bash
cd backend
python seed_campaigns.py
```

## 📡 API Endpoints

### Chat (Auto Campaign Fetch)
```bash
POST http://localhost:8000/api/v1/chat/message
POST http://localhost:8000/api/v1/chat/stream
```

### Campaigns (Direct Access)
```bash
GET  http://localhost:8000/api/v1/campaigns?user_id={uid}&status=ongoing
GET  http://localhost:8000/api/v1/campaigns/{id}?user_id={uid}
GET  http://localhost:8000/api/v1/campaigns/{id}/metrics?user_id={uid}
```

## 🎨 Frontend Usage

### Chat (streams automatically fetch campaigns)
```typescript
import { streamChatMessage } from '@/lib/api';

await streamChatMessage(
  {
    message: "How are my campaigns?",
    user_id: currentUser.uid
  },
  (chunk) => console.log(chunk),
  () => console.log('Done!')
);
```

### Direct Campaign Access
```typescript
import { getCampaigns } from '@/lib/api';

const { campaigns, metrics_summary } = await getCampaigns({
  user_id: currentUser.uid,
  status: 'ongoing'
});
```

## 🔍 What Gets Detected

### Status Keywords
```
ongoing  → status="ongoing"
paused   → status="paused"
active   → status="ongoing"
stopped  → status="paused"
```

### Platform Keywords
```
instagram   → platform="Instagram"
facebook    → platform="Facebook"
kol         → platform="KOL"
ecommerce   → platform="E-commerce"
```

### Intent Types
```
optimize/improve → optimization
analyze/performance → analysis
compare/vs → comparison
(default) → general
```

## 📈 Current Campaign Data

```
Total Campaigns: 10
- 7 ongoing (Valentine, Sneakers, Uni, KOL, Ramadan, Hoodies, CNY)
- 3 paused (Limited Edition, Weekend Sale, Winter Jackets)

Total Budget: $85,500
Total Spent: $57,200
Overall ROAS: 6.06x
Overall CTR: 4.82%
```

## 🎪 Example Response

**Query:** "How can I optimize my ongoing campaigns?"

**Response:**
```markdown
Based on your 7 ongoing campaigns with $53K budget:

## 🏆 Top Performers
1. Summer Sneakers (ROAS 8.25x) - Scale this!
2. Influencer KOL (ROAS 8.17x) - Increase budget

## ⚠️ Needs Work  
1. Flash Sale Hoodies (ROAS 5.68x) - Test new creative
2. Back to Uni (CTR 4.8%) - Improve ad copy

## 💰 Recommendations
• Shift budget from low to high performers
• A/B test underperforming campaigns
• Potential ROAS increase: +15%
```

## 🐛 Troubleshooting

### No campaigns returned?
```bash
# Check Firestore
python seed_campaigns.py

# Verify user_id matches
# Expected: "DT4DNex2L1N2rZ9kPddEzqougK22"
```

### Firebase not initialized?
```bash
# Check .env file has:
# FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, etc.
```

### TypeScript errors?
```bash
cd frontend
npm install
```

## 📚 Documentation

- **Full Guide:** [ORCHESTRATOR_IMPLEMENTATION.md](ORCHESTRATOR_IMPLEMENTATION.md)
- **Flow Diagram:** [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md)
- **Summary:** [SUMMARY.md](SUMMARY.md)
- **Examples:** [frontend/USAGE_EXAMPLES.ts](frontend/USAGE_EXAMPLES.ts)

## ✅ Checklist

- [ ] Backend running on :8000
- [ ] Frontend running on :3000
- [ ] Firebase credentials configured
- [ ] 10 campaigns seeded
- [ ] Test query works
- [ ] User ID in chat requests

## 🎯 Key Files

```
backend/app/services/
├── orchestrator_service.py  ← Intent analysis
├── campaign_service.py      ← Data fetching
└── chat_service.py          ← AI communication

backend/app/api/v1/routers/
├── chat.py                  ← Chat endpoints
└── campaigns.py             ← Campaign endpoints

frontend/lib/api/
├── chat.ts                  ← Chat client
├── campaigns.ts             ← Campaign client
└── index.ts                 ← Exports
```

## 🚀 You're All Set!

Just start backend + frontend, open chat, and ask:
**"How can I optimize my campaigns?"**

The AI will automatically fetch your data and provide recommendations! 🎉
