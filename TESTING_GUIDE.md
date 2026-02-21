# ROI Data Access - Testing Guide

## Quick Test Scenarios

### Test 1: Basic ROI Query
```
1. Login to the application
2. Go to chat interface
3. Type: "What was my ROI for the last 7 days?"
4. Expected: See approval dialog with detailed information
5. Click "Yes"
6. Expected: See ROI analysis with charts
```

### Test 2: Revenue Query
```
User Input: "Show me my revenue breakdown"
Expected: 
- Approval dialog appears
- Shows user's Gmail in the dialog
- After approval: Revenue charts and analysis
```

### Test 3: Video Performance Query
```
User Input: "Which video performed best this month?"
Expected:
- Approval dialog with data access details
- After approval: Best performing video analysis with metrics
```

### Test 4: Denial Flow
```
User Input: "What's my ROI?"
Actions: Click "No" on approval dialog
Expected: Supportive message without data access
Message: "I understand. I won't access your ROI data. Feel free to ask me anything else!"
```

### Test 5: Non-ROI Query
```
User Input: "How can I improve my marketing strategy?"
Expected: Direct response (NO approval dialog)
- This is not an ROI query
- No data access needed
- No approval required
```

## Verification Checklist

### Frontend Checks
- [ ] User email is retrieved from auth context
- [ ] User email is passed to backend in request
- [ ] Approval dialog appears for ROI queries
- [ ] "Yes" and "No" buttons work correctly
- [ ] Charts render after approval
- [ ] Console shows: "📧 [AUTH] User Gmail retrieved: user@example.com"

### Backend Checks
Look for these log messages:

```
✅ When ROI query detected:
🎯 [AGENT] Processing message with thread_id: xxx
   ↳ User email: user@example.com
   ↳ Message: What was my ROI...

⏸️ [HITL] Agent interrupted - tool execution requires approval
🔒 [HITL] Tool execution requires approval:
   ↳ Tool: roi_analysis
   ↳ Args: {"user_message": "...", "user_email": "user@example.com"}

✅ After user approves:
✅ [HITL] User approved - resuming agent execution
   ↳ User email for data access: user@example.com

🎯 [ROI TOOL] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 [ROI TOOL] Executing ROI Analysis (Post-Approval)
   ✓ User email: user@example.com
   ✓ Query: What was my ROI...
   ✓ Approval: GRANTED via LangGraph HITL
   ✓ Data source: Firebase ROI Collection
   ✓ Filter: user_email == 'user@example.com'

📊 [FIREBASE] Querying ROI collection
   ↳ Filter: user_email == 'user@example.com'
   ↳ Found X video(s) for user: user@example.com

✅ [ROI TOOL] Analysis completed successfully
   ↳ Charts generated: 3
```

### Firebase Data Checks
- [ ] ROI collection has documents with `user_email` field
- [ ] User's email matches Firebase Auth email
- [ ] Query filters correctly by user_email
- [ ] Only user's data is returned

## Sample Test Data

Add test data to Firebase ROI collection:

```json
{
  "user_email": "testuser@gmail.com",
  "title": "Test Video 1",
  "publish_date": "2026-02-15T10:00:00Z",
  "metrics": {
    "views": 10000,
    "likes": 500,
    "comments": 50,
    "retention_rate_percent": 45.2
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
    "promotion_cost_usd": 20.00
  },
  "roi_analysis": {
    "roi_percent": 150.5,
    "profit_usd": 150.50
  },
  "category": "Marketing"
}
```

## Expected Approval Dialog

```
🔒 ROI Data Access Request

I need your permission to access your ROI data from Firebase to answer your question:

> "What was my ROI for the last 7 days?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 What I'll Access:
- Video performance metrics (views, engagement, retention rates)
- Revenue breakdown (ad revenue, sponsorships, affiliate earnings)
- Cost analysis (production, promotion costs)
- ROI calculations and performance trends

🔐 Your Account:
- Gmail: user@example.com
- Data Source: Firebase ROI Collection
- Filter: user_email == 'user@example.com'

🛡️ Privacy & Security Guarantees:
- ✅ Isolated Data Access - Only YOUR data will be retrieved
- ✅ No Cross-User Access - Other users' data remains inaccessible
- ✅ Session-Only Usage - Data is used ONLY for this analysis
- ✅ No Storage - Retrieved data is not stored or cached
- ✅ No Sharing - Data is never shared with third parties
- ✅ You Control Access - You can deny this request

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Do you approve this data access?

[Yes] [No]
```

## Common Issues & Solutions

### Issue: Approval dialog not appearing
**Solution:** Check if ROI keywords are in the query
```
Good: "What's my ROI?"
Good: "Show revenue data"
Bad: "Tell me something" (no ROI keywords)
```

### Issue: "No user email" error
**Solution:** Ensure user is logged in
- Check Firebase Auth status
- Verify `user?.email` is not null
- Check console for auth warnings

### Issue: "No ROI data found"
**Solution:** Add test data to Firebase
- Ensure `user_email` field matches logged-in user
- Check Firebase console for documents
- Verify collection name is "ROI"

### Issue: Charts not rendering
**Solution:** Check response format
- Charts should be in `response.charts` array
- Each chart needs: type, title, data, config
- Check browser console for errors

## Performance Benchmarks

Expected response times:
- Approval request: < 2 seconds
- After approval (with data): 3-5 seconds
- Firebase query: < 1 second
- AI analysis: 2-4 seconds

## Security Testing

### Test User Isolation
1. Login as user A (userA@gmail.com)
2. Add ROI data for userA@gmail.com
3. Add ROI data for userB@gmail.com
4. Ask ROI query as user A
5. Verify: Only userA's data is returned

### Test Approval Required
1. Ask ROI query
2. Verify: Cannot proceed without approval
3. Cancel/deny approval
4. Verify: No data is accessed

### Test Authentication
1. Logout
2. Try to ask ROI query
3. Expected: Request fails or shows login prompt
4. Login required to access ROI data

## Success Criteria

✅ All tests pass
✅ Approval dialog shows for ROI queries
✅ User email correctly passed and filtered
✅ Only user's data is returned
✅ Charts render correctly
✅ Error handling works
✅ Logs show correct flow
✅ No security vulnerabilities
