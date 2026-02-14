# YouTube ROI Analytics Dashboard

## Overview
A comprehensive analytics dashboard for tracking and analyzing YouTube video Return on Investment (ROI). This feature provides detailed insights into revenue, costs, profitability, and performance metrics.

## Features

### 📊 Key Metrics Dashboard
- **Total Revenue**: Combined income from all revenue streams
- **Total Cost**: Production and promotion expenses
- **Net Profit**: Revenue minus costs
- **Overall ROI**: Percentage return on investment
- **Total Views**: Cumulative video views
- **Total Videos**: Number of published videos

### 📈 Visual Analytics
1. **Revenue vs Cost Trend** - Monthly bar chart comparing income and expenses
2. **Profit Trend** - Area chart showing profit over time
3. **Revenue Sources** - Pie chart breaking down:
   - Ad Revenue
   - Sponsorship Revenue
   - Affiliate Revenue
4. **Cost Breakdown** - Pie chart showing:
   - Production Costs
   - Promotion Costs

### 🏆 Performance Insights
- **Best Performing Video**: Highest ROI percentage
- **Most Viewed Video**: Maximum reach
- **Engagement Metrics**: Likes, comments, shares, retention rate, CTR

### 💡 Business Metrics
- Average ROI per video
- Revenue per view
- Cost per view
- Profit per view
- Subscriber growth
- Watch time analytics

## How to Use

### 1. Populate Sample Data (For Testing)
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the populate script
python populate_roi_data.py
```

The script will generate 15 sample YouTube videos with realistic metrics for the user `limjl0130@gmail.com`.

### 2. Access the Dashboard
1. Start both backend and frontend servers
2. Sign in to your account
3. Click the **ROI** icon in the sidebar (TrendingUp icon)
4. View your comprehensive analytics dashboard

### 3. API Endpoints

#### Get All Videos
```
GET /api/v1/roi/videos?limit=50&category=Education
Authorization: Bearer <token>
```

#### Get Analytics Summary
```
GET /api/v1/roi/analytics/summary?days=30
Authorization: Bearer <token>
```

#### Get Chart Data
```
GET /api/v1/roi/analytics/chart-data?chart_type=revenue_vs_cost
Authorization: Bearer <token>
```

Chart types:
- `revenue_vs_cost` - Monthly revenue and cost comparison
- `roi_trend` - ROI percentage over time
- `category_comparison` - Performance by video category
- `revenue_sources` - Revenue stream breakdown

## Data Structure

### Video Data Model
```typescript
{
  user_email: string
  video_id: string
  title: string
  category: string
  publish_date: string
  
  metrics: {
    views: number
    likes: number
    comments: number
    shares: number
    watch_time_hours: number
    retention_rate_percent: number
    subscribers_gained: number
    ctr_percent: number
  }
  
  costs: {
    production_cost_usd: number
    promotion_cost_usd: number
    total_cost_usd: number
  }
  
  revenue: {
    ad_revenue_usd: number
    sponsorship_revenue_usd: number
    affiliate_revenue_usd: number
    total_revenue_usd: number
  }
  
  roi_analysis: {
    roi_percent: number
    net_profit_usd: number
    revenue_per_view_usd: number
    cost_per_view_usd: number
  }
}
```

## Technical Stack

### Backend
- **FastAPI**: REST API endpoints
- **Firebase Firestore**: Database for storing video data
- **Python**: Data processing and calculations

### Frontend
- **Next.js 16**: React framework
- **Recharts**: Chart library for data visualization
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI components

## File Structure
```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           └── roi.py          # ROI API endpoints
│   └── core/
│       ├── firebase.py             # Firebase configuration
│       └── auth.py                 # Authentication
├── populate_roi_data.py            # Test data generator

frontend/
├── app/
│   └── roi/
│       ├── page.tsx                # ROI dashboard page
│       └── layout.tsx              # Layout wrapper
└── components/
    └── chat/
        └── sidebar.tsx             # Navigation (includes ROI link)
```

## Customization

### Modify Sample Data
Edit `populate_roi_data.py`:
```python
# Change user email
USER_EMAIL = "your-email@example.com"

# Change number of videos
NUM_VIDEOS = 20

# Modify cost ranges
production_cost = random.uniform(200, 2000)  # Increase costs
```

### Adjust Chart Colors
Edit `frontend/app/roi/page.tsx`:
```typescript
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
```

### Add More Metrics
1. Update the backend `roi.py` to calculate new metrics
2. Add new chart components in the frontend
3. Update the Analytics interface in TypeScript

## Business Use Cases

1. **Content Strategy**: Identify which video categories generate highest ROI
2. **Budget Allocation**: Understand production vs promotion cost effectiveness
3. **Revenue Optimization**: Analyze which revenue streams are most profitable
4. **Performance Tracking**: Monitor trends and adjust strategy accordingly
5. **Investment Decisions**: Make data-driven decisions on video production

## Security
- All endpoints require Firebase authentication
- User data is isolated (users can only see their own videos)
- Token-based authorization for API access

## Future Enhancements
- [ ] Export reports to PDF/Excel
- [ ] Real-time YouTube API integration
- [ ] Predictive analytics using ML
- [ ] Goal setting and tracking
- [ ] Competitor comparison
- [ ] Custom date range filters
- [ ] Video-level detailed view

## Support
For issues or questions, please check:
1. Backend server is running on port 8000
2. Frontend server is running on port 3000
3. Firebase credentials are properly configured
4. User is authenticated with valid token
