# ROI Chatbot Orchestrator Documentation

## Overview

The chatbot on the chat page now acts as an orchestrator that can analyze ROI data and display meaningful charts based on user queries. When users ask questions about their ROI performance, the chatbot automatically fetches data from Firebase, analyzes it, and presents both textual insights and interactive charts.

## Features

### 1. **Intelligent ROI Query Detection**
The system automatically detects when users ask ROI-related questions using keywords like:
- ROI, revenue, profit, cost, earnings
- Performance, analytics, metrics
- Views, videos, content, engagement
- Time periods: "7 days ago", "last week", "last month"

### 2. **Time-Based Analysis**
Users can query ROI data for specific time periods:
- "What is my ROI in the last 7 days?"
- "Show me my performance over the past 30 days"
- "How did my videos perform last week?"

### 3. **Interactive Charts**
The system generates multiple chart types automatically:

#### **Bar Charts**
- Revenue vs Cost vs Profit Overview
- Category Performance (Average ROI by category)

#### **Line Charts**
- ROI & Profit Trend Over Time
- Shows how performance changes day by day

#### **Pie Charts**
- Revenue Sources Breakdown (Ad Revenue, Sponsorships, Affiliates)

### 4. **Comprehensive Analytics**
Each ROI query provides:
- Total videos analyzed
- Total views, revenue, cost, and profit
- Overall ROI percentage
- Best performing video
- Engagement metrics (likes, comments, retention)
- Category-wise performance
- Time-based trends

## Architecture

### Backend Components

#### 1. **ROI Analysis Service** (`roi_analysis_service.py`)
Core service that handles:
- Query detection and time period extraction
- Data fetching from Firebase ROI collection
- Data analysis and metric calculation
- Chart configuration generation
- Text summary generation

Key methods:
- `detect_roi_query()` - Identifies ROI-related queries
- `extract_time_period()` - Extracts time range from user message
- `fetch_user_roi_data()` - Gets ROI data from Firebase
- `analyze_roi_data()` - Performs comprehensive analysis
- `generate_chart_config()` - Creates chart configurations
- `process_roi_query()` - Main orchestration method

#### 2. **Enhanced Chat Service** (`chat_service.py`)
Updated to integrate ROI analysis:
- Detects ROI queries using the ROI analysis service
- Fetches and analyzes user's ROI data
- Returns structured response with text and charts
- Falls back to normal AI chat for non-ROI queries

#### 3. **Updated Schemas** (`chat.py`)
New models:
- `ChartConfig` - Defines chart structure and data
- Updated `ChatRequest` - Now includes `user_email` field
- Updated `ChatResponse` - Now includes optional `charts` array

### Frontend Components

#### 1. **ROI Chart Component** (`roi-chart.tsx`)
Renders different chart types using Recharts:
- Supports bar, line, and pie charts
- Responsive design
- Theme-aware (light/dark mode)
- Customizable colors and labels

#### 2. **Enhanced Message Bubble** (`message-bubble.tsx`)
- Displays markdown-formatted text
- Renders charts below the message content
- Maintains existing user/assistant styling

#### 3. **Updated Chat Area** (`chat-area.tsx`)
- Passes user email to API for ROI data access
- Handles chart data in responses
- Displays charts inline with messages

#### 4. **Updated API Client** (`chat.ts`)
- Added `ChartConfig` interface
- Updated request to include `user_email`
- Updated response to include optional `charts` array

## Usage Examples

### Example Queries

1. **General ROI Overview**
   ```
   User: "What is my ROI?"
   Bot: [Displays comprehensive analysis with multiple charts]
   ```

2. **Time-Specific Query**
   ```
   User: "What is my ROI in the last 7 days?"
   Bot: [Shows analysis for videos published in last 7 days]
   ```

3. **Performance Trends**
   ```
   User: "Show me my revenue trends over the past month"
   Bot: [Displays trend analysis with line charts]
   ```

4. **Category Analysis**
   ```
   User: "Which video categories perform best?"
   Bot: [Shows category breakdown with comparative charts]
   ```

### Sample Response Structure

```json
{
  "message": "## 📊 ROI Analysis for the last 7 days\n\n### Overall Performance\n- **Total Videos**: 5\n...",
  "charts": [
    {
      "type": "bar",
      "title": "Revenue, Cost & Profit Overview",
      "data": [...],
      "xKey": "name",
      "yKey": "value"
    },
    {
      "type": "line",
      "title": "ROI & Profit Trend Over Time",
      "data": [...],
      "xKey": "date",
      "lines": [...]
    }
  ]
}
```

## Data Flow

1. **User asks ROI question** → Chat Area Component
2. **Message sent to backend** → Including user email
3. **Chat service receives message** → Checks if ROI-related
4. **If ROI query:**
   - ROI Analysis Service fetches data from Firebase
   - Analyzes data and calculates metrics
   - Generates chart configurations
   - Creates formatted text summary
5. **Response returned** → Text + Charts
6. **Frontend renders:**
   - Markdown-formatted text in message bubble
   - Interactive charts below the text

## Configuration

### Backend Setup

1. Ensure Firebase is properly configured in `core/firebase.py`
2. ROI collection must exist in Firestore with proper structure
3. User email must match the `user_email` field in ROI documents

### Frontend Setup

1. Recharts library must be installed (already in dependencies)
2. Chart component uses theme variables from Tailwind
3. Authentication context must provide user email

## ROI Data Structure

The system expects ROI documents in Firebase with this structure:

```javascript
{
  user_email: "user@example.com",
  video_id: "VIDEO_001_1234",
  title: "Video Title",
  category: "Education",
  publish_date: "2026-02-08T10:30:00",
  metrics: {
    views: 50000,
    likes: 2500,
    comments: 150,
    shares: 300,
    watch_time_hours: 1500.5,
    retention_rate_percent: 65.5,
    subscribers_gained: 1250
  },
  costs: {
    production_cost_usd: 500.00,
    promotion_cost_usd: 250.00,
    total_cost_usd: 750.00
  },
  revenue: {
    ad_revenue_usd: 2500.00,
    sponsorship_revenue_usd: 3000.00,
    affiliate_revenue_usd: 500.00,
    total_revenue_usd: 6000.00,
    cpm_usd: 5.00
  },
  roi_analysis: {
    roi_percent: 700.00,
    net_profit_usd: 5250.00,
    revenue_per_view_usd: 0.12,
    cost_per_view_usd: 0.015,
    profit_per_view_usd: 0.105
  }
}
```

## Testing

### Test the ROI Orchestrator

1. **Populate Test Data:**
   ```bash
   cd backend
   python populate_roi_data.py
   ```
   Enter your email when prompted.

2. **Start Backend:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Test Queries:**
   - Go to the Chat page
   - Try queries like:
     - "What is my ROI in the last 7 days?"
     - "Show me my revenue breakdown"
     - "How are my videos performing?"
     - "What's my best performing video?"

## Benefits

✅ **No Changes to ROI Page** - The ROI page remains unchanged as requested

✅ **Chat-Based Interface** - Users can ask natural language questions

✅ **Visual Insights** - Charts make data easier to understand

✅ **Context-Aware** - System understands time periods and specific queries

✅ **Comprehensive Analysis** - Provides both high-level and detailed insights

✅ **Extensible** - Easy to add more chart types or analysis methods

## Future Enhancements

- Add more chart types (area charts, scatter plots)
- Support comparison between time periods
- Add AI-powered recommendations based on ROI data
- Export charts as images
- Save and share analysis reports
- Real-time data updates with WebSocket

## Troubleshooting

### No Charts Displayed
- Ensure user is authenticated and email is available
- Check that ROI data exists in Firebase for the user
- Verify Firebase connection in backend

### Incorrect Data
- Check the ROI document structure matches expected format
- Ensure `user_email` field matches authenticated user's email
- Verify date formats are ISO 8601 compliant

### Chart Rendering Issues
- Check browser console for errors
- Ensure Recharts library is properly installed
- Verify theme CSS variables are defined

## Support

For issues or questions, refer to:
- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser developer console
- Firebase console: Verify data structure and user access
