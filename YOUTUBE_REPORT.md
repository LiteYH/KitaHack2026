# 🎬 YouTube ROI Report Generator

## Quick Links

- 📖 [Full Documentation](./YOUTUBE_REPORT_README.md)
- 🚀 [Quick Start Guide](./YOUTUBE_REPORT_QUICKSTART.md)
- 💻 [Implementation Details](./YOUTUBE_REPORT_IMPLEMENTATION.md)

## What is This?

A complete YouTube ROI analytics system that:
- 📊 Fetches YouTube metrics from Firestore
- 🤖 Analyzes performance using Google Gemini AI
- 📄 Generates professional reports (HTML, PDF, Text, JSON)
- 🌐 Provides REST API and web interface

## Features

✅ AI-powered insights and recommendations  
✅ Multi-format report generation (HTML, PDF, Text, JSON)  
✅ Real-time data from Firestore  
✅ Professional report templates  
✅ REST API for integration  
✅ Modern React frontend  
✅ Sample data generator  

## Quick Setup

### 1. Install Dependencies
```bash
cd backend
pip install firebase-admin google-generativeai langchain-google-genai xhtml2pdf beautifulsoup4
```

### 2. Configure (backend/.env)
```env
FIREBASE_PROJECT_ID=kitahack2026-8feed
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@project.iam.gserviceaccount.com
GOOGLE_API_KEY=your-gemini-api-key
```

### 3. Add Sample Data
```bash
cd backend
python populate_youtube_data.py 50
```

### 4. Run Services
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Access
- 🌐 Frontend: http://localhost:3000/youtube-report
- 🔌 API: http://localhost:8000/api/v1/youtube-report/preview

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/preview` | Quick data statistics |
| POST | `/generate` | Generate full report |
| GET | `/download/html` | Download HTML report |
| GET | `/download/pdf` | Download PDF report |
| GET | `/download/text` | Download text report |
| GET | `/download/json` | Download JSON data |

## Firestore Data Structure

```json
{
  "user_id": "user123",
  "platform": "YouTube",
  "video_title": "Video Title",
  "content_category": "Tutorial",
  "views": 125000,
  "likes": 8500,
  "comments": 1200,
  "shares": 450,
  "subscribers_gained": 350,
  "watch_time_hours": 4200,
  "ad_spend": 500.00,
  "revenue_generated": 1850.00,
  "created_at": "2026-01-15T10:30:00Z"
}
```

## Report Contents

1. **Executive Summary** - High-level performance overview
2. **Key Metrics** - ROI, revenue, views, engagement
3. **Category Analysis** - Performance by content type
4. **Top Videos** - Best performing content
5. **AI Insights** - Recommendations and strategies
6. **Growth Plan** - 30/60/90-day roadmap

## Files Created

### Backend
- `app/core/firestore_client.py` - Firebase/Firestore client
- `app/services/youtube_report/youtube_ai_agent.py` - AI analysis agent
- `app/services/youtube_report/youtube_pdf_generator.py` - PDF generator
- `app/api/v1/routers/youtube_report.py` - API endpoints
- `populate_youtube_data.py` - Sample data generator

### Frontend
- `app/youtube-report/page.tsx` - Report generator UI

### Documentation
- `YOUTUBE_REPORT_README.md` - Full documentation
- `YOUTUBE_REPORT_QUICKSTART.md` - Quick setup guide
- `YOUTUBE_REPORT_IMPLEMENTATION.md` - Implementation details
- `test_youtube_report.bat` - Windows test script

## Testing

### Windows
```bash
test_youtube_report.bat
```

### Manual
```bash
# Test Firestore
cd backend
python -c "from app.core.firestore_client import firestore_client; import asyncio; print(asyncio.run(firestore_client.get_collection_stats('roi_metrics')))"

# Test AI Agent
python -m app.services.youtube_report.youtube_ai_agent

# Test PDF Generator
python -m app.services.youtube_report.youtube_pdf_generator

# Test API
curl http://localhost:8000/api/v1/youtube-report/preview
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Firestore  │────▶│  AI Agent    │────▶│ PDF Generator│
│  Database   │     │  (Gemini)    │     │  (xhtml2pdf) │
└─────────────┘     └──────────────┘     └──────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌──────────────┐
                    │  API Router  │────▶│   Frontend   │
                    │  (FastAPI)   │     │    (React)   │
                    └──────────────┘     └──────────────┘
```

## Technologies

**Backend:**
- Python 3.10+
- FastAPI
- Firebase Admin SDK
- Google Gemini AI
- xhtml2pdf
- BeautifulSoup4

**Frontend:**
- Next.js 14
- React
- TypeScript
- shadcn/ui
- Tailwind CSS

## Requirements

### Python Packages
```
firebase-admin>=6.5.0
google-generativeai>=0.3.0
langchain-google-genai>=4.2.0
xhtml2pdf>=0.2.13
beautifulsoup4>=4.12.0
```

### Environment Variables
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `GOOGLE_API_KEY`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Firebase connection failed | Check `.env` credentials |
| No data found | Run `populate_youtube_data.py` |
| PDF generation failed | Install: `pip install xhtml2pdf` |
| AI not working | Verify `GOOGLE_API_KEY` |

## Sample Data

Generate 50 sample YouTube records:
```bash
cd backend
python populate_youtube_data.py 50
```

Clear sample data:
```bash
python populate_youtube_data.py clear
```

## Performance

- Data fetch: ~1-2 seconds
- AI analysis: ~10-30 seconds
- PDF conversion: ~2-5 seconds
- **Total: ~15-40 seconds per report**

## Security

✅ Firebase credentials in `.env` (never commit)  
✅ API keys server-side only  
✅ User ID filtering for access control  
✅ CORS configured properly  

## Future Enhancements

- [ ] Date range filtering
- [ ] Multi-period comparison
- [ ] Excel export
- [ ] Email scheduling
- [ ] Real-time dashboard
- [ ] Custom branding
- [ ] Multi-language support

## Support

See detailed documentation:
- [YOUTUBE_REPORT_README.md](./YOUTUBE_REPORT_README.md) - Complete guide
- [YOUTUBE_REPORT_QUICKSTART.md](./YOUTUBE_REPORT_QUICKSTART.md) - Setup steps
- [YOUTUBE_REPORT_IMPLEMENTATION.md](./YOUTUBE_REPORT_IMPLEMENTATION.md) - Technical details

## License

Part of BOS Solution KitaHack 2026 project.

---

**Created:** February 14, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
