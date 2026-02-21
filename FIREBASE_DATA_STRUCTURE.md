# Firebase ROI Collection - Required Data Structure

## Current Issue
Your Firebase document has a **flat structure**, but the code expects a **nested structure**.

## ❌ Current Structure (From Screenshot)
```json
{
  "user_email": "limjl0130@gmail.com",
  "video_id": "VIDEO_011_4375",
  "title": "Ultimate Guide to Digital Marketing in 2026",
  "roi_percent": 380.88,
  "revenue_per_view_usd": 0.0357,
  "profit_per_view_usd": 0.0283,
  "status": "published",
  "tags": ["business", "entrepreneurship", "marketing", "growth"]
}
```

## ✅ Required Structure (Expected by Code)
```json
{
  "user_email": "limjl0130@gmail.com",
  "video_id": "VIDEO_011_4375",
  "title": "Ultimate Guide to Digital Marketing in 2026",
  "publish_date": "2026-02-15T10:00:00Z",
  "category": "Marketing",
  "status": "published",
  "tags": ["business", "entrepreneurship", "marketing", "growth"],
  
  "metrics": {
    "views": 50000,
    "likes": 2500,
    "comments": 180,
    "shares": 450,
    "retention_rate_percent": 65.5,
    "avg_watch_time_seconds": 420
  },
  
  "revenue": {
    "total_revenue_usd": 1785.00,
    "ad_revenue_usd": 1200.00,
    "sponsorship_revenue_usd": 500.00,
    "affiliate_revenue_usd": 85.00
  },
  
  "costs": {
    "total_cost_usd": 450.00,
    "production_cost_usd": 300.00,
    "promotion_cost_usd": 100.00,
    "equipment_cost_usd": 50.00
  },
  
  "roi_analysis": {
    "roi_percent": 296.67,
    "profit_usd": 1335.00,
    "profit_per_view_usd": 0.0267,
    "revenue_per_view_usd": 0.0357,
    "cpm_usd": 24.00
  }
}
```

## Quick Fix: Update Your Firebase Document

### Option 1: Update Existing Document
In Firebase Console:
1. Click on the document `2ifXAckhxLNDmlvt3oEC`
2. Add these nested fields:

```javascript
// Add metrics object
metrics: {
  views: 50000,           // Estimate based on your revenue
  likes: 2500,            // ~5% of views
  comments: 180,          // ~0.36% of views
  shares: 450,            // ~0.9% of views
  retention_rate_percent: 65.5,
  avg_watch_time_seconds: 420
}

// Add revenue object
revenue: {
  total_revenue_usd: (50000 * 0.0357),  // views * revenue_per_view
  ad_revenue_usd: (50000 * 0.0357 * 0.7),  // 70% from ads
  sponsorship_revenue_usd: (50000 * 0.0357 * 0.25),  // 25% from sponsorship
  affiliate_revenue_usd: (50000 * 0.0357 * 0.05)   // 5% from affiliate
}

// Add costs object
costs: {
  total_cost_usd: (50000 * (0.0357 - 0.0283)),  // Calculated from profit margin
  production_cost_usd: (50000 * (0.0357 - 0.0283) * 0.7),
  promotion_cost_usd: (50000 * (0.0357 - 0.0283) * 0.2),
  equipment_cost_usd: (50000 * (0.0357 - 0.0283) * 0.1)
}

// Update roi_analysis to be nested
roi_analysis: {
  roi_percent: 380.88,
  profit_usd: (50000 * 0.0283),
  profit_per_view_usd: 0.0283,
  revenue_per_view_usd: 0.0357,
  cpm_usd: (0.0357 * 1000)
}

// Add publish_date
publish_date: "2026-02-15T10:00:00Z"

// Keep existing fields
// user_email, video_id, title, status, tags remain the same
```

### Option 2: Complete Example Document

Copy this JSON and create a new test document in Firebase:

```json
{
  "user_email": "limjl0130@gmail.com",
  "video_id": "VIDEO_TEST_001",
  "title": "Test Video - Marketing Guide",
  "publish_date": "2026-02-15T10:00:00Z",
  "category": "Marketing",
  "status": "published",
  "tags": ["marketing", "business"],
  
  "metrics": {
    "views": 10000,
    "likes": 500,
    "comments": 50,
    "shares": 100,
    "retention_rate_percent": 45.2,
    "avg_watch_time_seconds": 300
  },
  
  "revenue": {
    "total_revenue_usd": 250.50,
    "ad_revenue_usd": 200.00,
    "sponsorship_revenue_usd": 50.50,
    "affiliate_revenue_usd": 0
  },
  
  "costs": {
    "total_cost_usd": 100.00,
    "production_cost_usd": 80.00,
    "promotion_cost_usd": 20.00,
    "equipment_cost_usd": 0
  },
  
  "roi_analysis": {
    "roi_percent": 150.5,
    "profit_usd": 150.50,
    "profit_per_view_usd": 0.01505,
    "revenue_per_view_usd": 0.02505,
    "cpm_usd": 25.05
  }
}
```

## Testing After Update

1. Update your Firebase document with the nested structure
2. Restart your backend (if needed)
3. Ask: "What was my ROI?"
4. You should now see the analysis with charts!

## Alternative: Modify Code to Handle Flat Structure

If you prefer to keep your flat structure, I can modify the code to handle both formats. Let me know!
