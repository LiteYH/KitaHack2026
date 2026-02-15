# YouTube ROI Report Generator - Quick Setup

## Step 1: Install Backend Dependencies

```bash
cd backend
pip install firebase-admin google-generativeai langchain-google-genai xhtml2pdf beautifulsoup4
```

## Step 2: Configure Environment Variables

Create or update `backend/.env`:

```env
# Firebase Admin SDK
FIREBASE_PROJECT_ID=kitahack2026-8feed
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@kitahack2026-8feed.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Google AI
GOOGLE_API_KEY=your-gemini-api-key
```

## Step 3: Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **kitahack2026-8feed**
3. Click ⚙️ (Settings) → Project Settings
4. Navigate to "Service Accounts" tab
5. Click "Generate New Private Key"
6. Save the JSON file
7. Extract these values to `.env`:
   - `project_id` → `FIREBASE_PROJECT_ID`
   - `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
   - `private_key` → `FIREBASE_PRIVATE_KEY` (keep \n)
   - `client_email` → `FIREBASE_CLIENT_EMAIL`
   - `client_id` → `FIREBASE_CLIENT_ID`

## Step 4: Get Google AI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Add to `.env` as `GOOGLE_API_KEY`

## Step 5: Add Sample YouTube Data (Optional)

Add sample data to Firestore `roi_metrics` collection:

```javascript
// Firebase Console → Firestore Database → roi_metrics → Add Document
{
  "user_id": "demo_user",
  "platform": "YouTube",
  "video_title": "Ultimate Marketing Tutorial",
  "content_category": "Tutorial",
  "views": 125000,
  "likes": 8500,
  "comments": 1200,
  "shares": 450,
  "subscribers_gained": 350,
  "watch_time_hours": 4200,
  "ad_spend": 500.00,
  "revenue_generated": 1850.00,
  "created_at": new Date()
}
```

## Step 6: Test Backend

```bash
# Test Firestore connection
cd backend
python -c "from app.core.firestore_client import firestore_client; import asyncio; print(asyncio.run(firestore_client.get_collection_stats('roi_metrics')))"

# Test AI agent
python -m app.services.youtube_report.youtube_ai_agent

# Test full generator
python -m app.services.youtube_report.youtube_pdf_generator
```

## Step 7: Start Services

Terminal 1 (Backend):
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

## Step 8: Access Report Generator

Open browser: [http://localhost:3000/youtube-report](http://localhost:3000/youtube-report)

## API Endpoints

- **Preview**: GET `http://localhost:8000/api/v1/youtube-report/preview`
- **Generate**: POST `http://localhost:8000/api/v1/youtube-report/generate`
- **Download HTML**: GET `http://localhost:8000/api/v1/youtube-report/download/html`
- **Download PDF**: GET `http://localhost:8000/api/v1/youtube-report/download/pdf`

## Test with cURL

```bash
# Preview data
curl http://localhost:8000/api/v1/youtube-report/preview

# Generate report
curl -X POST http://localhost:8000/api/v1/youtube-report/generate

# Download HTML
curl -O http://localhost:8000/api/v1/youtube-report/download/html

# Download PDF
curl -O http://localhost:8000/api/v1/youtube-report/download/pdf
```

## Troubleshooting

### Issue: Firebase connection failed
**Solution**: 
- Verify `.env` file exists in `backend/` directory
- Check Firebase credentials are correct
- Ensure private key has proper `\n` formatting

### Issue: No data found
**Solution**:
- Add sample data to Firestore (see Step 5)
- Check collection name is exactly `roi_metrics`
- Verify documents have required fields

### Issue: PDF generation failed
**Solution**:
- Install xhtml2pdf: `pip install xhtml2pdf==0.2.13`
- HTML format will still work
- Check console for specific errors

### Issue: AI not generating analysis
**Solution**:
- Verify `GOOGLE_API_KEY` in `.env`
- Check API key is valid at [Google AI Studio](https://makersuite.google.com)
- System will use basic analysis as fallback

## Required Python Packages

```txt
firebase-admin>=6.0.0
google-generativeai>=0.3.0
langchain-google-genai>=0.0.5
xhtml2pdf>=0.2.13
beautifulsoup4>=4.12.0
```

## Required Firestore Fields

**Minimum Required:**
- `views` (number)
- `likes` (number)
- `comments` (number)
- `shares` (number)
- `ad_spend` (number)
- `revenue_generated` (number)
- `created_at` (timestamp)

**Optional but Recommended:**
- `user_id` (string)
- `video_title` (string)
- `content_category` (string)
- `subscribers_gained` (number)
- `watch_time_hours` (number)

## Success Indicators

✅ Backend running on `http://localhost:8000`
✅ Frontend running on `http://localhost:3000`
✅ Preview shows data count > 0
✅ Report generation completes without errors
✅ Downloads work for all formats

## Next Steps

1. Add more YouTube data to Firestore
2. Customize report templates
3. Adjust AI analysis prompts
4. Add navigation links to main app
5. Set up production deployment

For detailed documentation, see [YOUTUBE_REPORT_README.md](./YOUTUBE_REPORT_README.md)
