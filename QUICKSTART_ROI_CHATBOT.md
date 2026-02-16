# 🚀 ROI Chatbot Orchestrator - Quick Start Guide

## ✅ Implementation Complete

Your chatbot now acts as an intelligent orchestrator that analyzes ROI data and displays interactive charts in the chat interface!

## 🎯 What Was Built

### Backend (Python/FastAPI)
✅ **ROI Analysis Service** - Intelligent query detection and data analysis
✅ **Enhanced Chat Service** - Integrated ROI capabilities with Gemini AI
✅ **Updated API Schemas** - Support for chart data in responses
✅ **Chart Generation** - Automatic creation of bar, line, and pie charts

### Frontend (Next.js/React)
✅ **ROI Chart Component** - Beautiful, responsive charts using Recharts
✅ **Enhanced Message Bubble** - Displays charts inline with messages
✅ **Updated Chat Area** - Passes user email for ROI data access
✅ **Updated Suggestion Cards** - Added ROI query examples

## 🎬 How to Use

### Step 1: Populate Test Data (if not already done)

```powershell
cd "c:\Users\morei\OneDrive\Desktop\Project\Kitahack 2026\KitaHack2026\backend"
.\.venv\Scripts\python.exe populate_roi_data.py
```

Enter your email when prompted. This creates sample ROI data for testing.

### Step 2: Test the Backend

```powershell
cd "c:\Users\morei\OneDrive\Desktop\Project\Kitahack 2026\KitaHack2026\backend"
.\.venv\Scripts\python.exe test_roi_orchestrator.py
```

This verifies that the ROI orchestrator is working correctly.

### Step 3: Start the Application

**Terminal 1 - Backend:**
```powershell
cd "c:\Users\morei\OneDrive\Desktop\Project\Kitahack 2026\KitaHack2026\backend"
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd "c:\Users\morei\OneDrive\Desktop\Project\Kitahack 2026\KitaHack2026\frontend"
npm run dev
```

### Step 4: Try It Out!

1. Open your browser to the frontend URL (typically `http://localhost:3000`)
2. Navigate to the **Chat** page
3. Ask ROI questions like:
   - "What is my ROI in the last 7 days?"
   - "Show me my revenue breakdown"
   - "How are my videos performing?"
   - "What's my best performing video?"
   - "Show me my performance trends over time"

## 📊 Example Queries

### Time-Based Queries
- "What is my ROI in the last 7 days?"
- "Show me my performance for the past 30 days"
- "How did my videos do last week?"
- "What's my ROI last month?"

### Performance Queries
- "Show me my revenue breakdown"
- "What's my total profit?"
- "How are my videos performing?"
- "Which category performs best?"

### Specific Queries
- "What's my best performing video?"
- "Show me my revenue vs cost"
- "How much did I earn from sponsorships?"
- "What's my average ROI?"

## 🎨 What You'll See

When you ask an ROI question, the chatbot will:

1. **Analyze Your Data** - Fetch ROI data from Firebase
2. **Generate Insights** - Calculate metrics, trends, and comparisons
3. **Display Text Summary** - Formatted markdown with key metrics
4. **Show Interactive Charts**:
   - 📊 Revenue vs Cost vs Profit (Bar Chart)
   - 🥧 Revenue Sources Breakdown (Pie Chart)
   - 📈 ROI & Profit Trend Over Time (Line Chart)
   - 📊 Category Performance (Bar Chart)

## 🔧 Architecture

```
User Question → Chat API
              ↓
       ROI Query Detection
              ↓
    Fetch Data from Firebase
              ↓
     Analyze & Calculate Metrics
              ↓
    Generate Charts & Summary
              ↓
    Return to Frontend
              ↓
    Render Text + Charts
```

## 📁 Key Files Modified/Created

### Backend
- `app/services/roi_analysis_service.py` - **NEW** - Core ROI analysis logic
- `app/services/chat_service.py` - Enhanced with ROI integration
- `app/schemas/chat.py` - Added ChartConfig schema
- `app/api/v1/routers/chat.py` - Updated to handle charts
- `test_roi_orchestrator.py` - **NEW** - Test script

### Frontend
- `components/chat/roi-chart.tsx` - **NEW** - Chart rendering component
- `components/chat/message-bubble.tsx` - Enhanced to display charts
- `components/chat/chat-area.tsx` - Updated to pass user email
- `components/chat/suggestion-cards.tsx` - Added ROI examples
- `lib/api/chat.ts` - Updated API client with chart support

## ✨ Features

### Intelligent Query Detection
- Automatically detects ROI-related questions
- Extracts time periods from natural language
- Falls back to normal chat for non-ROI queries

### Comprehensive Analytics
- Total videos, views, revenue, cost, profit
- Overall ROI percentage with performance indicators
- Best performing video analysis
- Engagement metrics (likes, comments, retention)
- Category-wise performance breakdown
- Time-based trends and patterns

### Visual Charts
- **Bar Charts** - Compare revenue, cost, profit; category performance
- **Line Charts** - Show trends over time (ROI, profit)
- **Pie Charts** - Revenue sources breakdown
- Responsive design that adapts to screen size
- Theme-aware (works in light/dark mode)

## 🔒 Important Notes

✅ **ROI Page Unchanged** - The ROI dashboard page remains exactly as it was
✅ **User Privacy** - Only fetches data for the authenticated user
✅ **Real-time** - Always uses the latest data from Firebase
✅ **Extensible** - Easy to add new chart types or metrics

## 🧪 Testing Checklist

- [ ] Test data populated in Firebase
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] User can authenticate
- [ ] Chat accepts messages
- [ ] ROI queries return charts
- [ ] Charts render correctly
- [ ] Non-ROI queries work normally

## 🐛 Troubleshooting

### No Charts Displayed
- Ensure you're logged in with the same email used in ROI data
- Check Firebase console to verify ROI collection exists
- Check browser console for errors

### Backend Errors
- Make sure you're using the venv: `.\.venv\Scripts\python.exe`
- Verify GOOGLE_API_KEY is set in `.env`
- Check Firebase credentials are valid

### Frontend Errors
- Clear browser cache and reload
- Check that Recharts is installed: `npm install recharts`
- Verify user is authenticated

## 📚 Additional Documentation

For detailed technical documentation, see:
- `ROI_CHATBOT_DOCUMENTATION.md` - Full technical documentation

## 🎉 Success!

You now have a powerful AI chatbot that can:
- Answer marketing questions
- Analyze ROI data on-demand
- Generate beautiful visualizations
- Provide actionable insights

**Try it now and see your ROI data come to life!** 🚀
