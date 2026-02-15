# YouTube ROI Report Generator

## Overview

A comprehensive system for generating AI-powered YouTube ROI analysis reports from Firestore data. The system fetches YouTube metrics, analyzes performance using Google Gemini AI, and generates professional reports in multiple formats (HTML, PDF, Text, JSON).

## Architecture

### Backend Components

1. **Firestore Client** (`app/core/firestore_client.py`)
   - Connects to Firebase/Firestore using Admin SDK
   - Fetches YouTube ROI metrics from the `roi_metrics` collection
   - Supports filtering by user ID

2. **YouTube AI Agent** (`app/services/youtube_report/youtube_ai_agent.py`)
   - Analyzes YouTube ROI data using Google Gemini 2.0 Flash
   - Generates comprehensive insights and recommendations
   - Produces HTML reports optimized for PDF conversion

3. **YouTube PDF Generator** (`app/services/youtube_report/youtube_pdf_generator.py`)
   - Orchestrates the report generation flow
   - Converts HTML to PDF using xhtml2pdf
   - Provides multiple output formats

4. **API Router** (`app/api/v1/routers/youtube_report.py`)
   - RESTful API endpoints for report generation
   - Supports download in HTML, PDF, Text, and JSON formats
   - Includes preview endpoint for quick data checks

### Frontend Component

**YouTube Report Page** (`frontend/app/youtube-report/page.tsx`)
- Modern React interface with shadcn/ui components
- Two-tab interface: Preview and Full Report
- Download reports in multiple formats
- Real-time report generation with loading states

## Installation

### Backend Setup

1. **Install Required Python Packages**

```bash
cd backend
pip install firebase-admin google-generativeai langchain-google-genai xhtml2pdf beautifulsoup4
```

Or add to `requirements.txt`:
```
firebase-admin>=6.0.0
google-generativeai>=0.3.0
langchain-google-genai>=0.0.5
xhtml2pdf>=0.2.13
beautifulsoup4>=4.12.0
```

2. **Configure Environment Variables**

Add to `.env` file:
```env
# Firebase Admin SDK
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-client-email@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Google AI
GOOGLE_API_KEY=your-gemini-api-key
```

3. **Get Firebase Service Account Credentials**

   a. Go to Firebase Console → Project Settings → Service Accounts
   b. Click "Generate New Private Key"
   c. Download the JSON file
   d. Extract values and add to `.env`:
      - `project_id` → `FIREBASE_PROJECT_ID`
      - `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
      - `private_key` → `FIREBASE_PRIVATE_KEY` (keep the newlines as `\n`)
      - `client_email` → `FIREBASE_CLIENT_EMAIL`
      - `client_id` → `FIREBASE_CLIENT_ID`

4. **Get Google AI API Key**

   a. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   b. Create new API key
   c. Add to `.env` as `GOOGLE_API_KEY`

### Frontend Setup

The frontend uses your existing Next.js setup. No additional packages required if you already have shadcn/ui installed.

## Firestore Data Structure

### Collection: `roi_metrics`

Expected document structure for YouTube data:

```json
{
  "user_id": "user123",
  "platform": "YouTube",
  "video_title": "How to Create Amazing Content",
  "content_category": "Tutorial",
  "content_type": "Video",
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

### Required Fields
- `views` (integer): Video views
- `likes` (integer): Number of likes
- `comments` (integer): Number of comments
- `shares` (integer): Number of shares
- `ad_spend` (float): Marketing spend
- `revenue_generated` (float): Revenue from video
- `created_at` (timestamp): Record date

### Optional Fields
- `user_id` (string): Filter by user
- `video_title` (string): Video name
- `content_category` (string): Category (Tutorial, Review, Vlog, etc.)
- `subscribers_gained` (integer): New subscribers
- `watch_time_hours` (float): Total watch time

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/youtube-report
```

### 1. Preview Data
**GET** `/preview?user_id={optional}`

Get quick statistics without generating full report.

**Response:**
```json
{
  "success": true,
  "message": "YouTube report preview generated",
  "data": {
    "record_count": 47,
    "has_data": true,
    "preview": {
      "total_views": 370000,
      "total_revenue": 13500.00,
      "total_ad_spend": 3680.00,
      "overall_roi": 266.85
    }
  }
}
```

### 2. Generate Report
**POST** `/generate?user_id={optional}`

Generate full report with AI analysis.

**Response:**
```json
{
  "success": true,
  "message": "YouTube ROI report generated successfully",
  "data": {
    "html": "<html>...</html>",
    "pdf_base64": "JVBERi0xLjQ...",
    "text": "YouTube ROI Report...",
    "json": "{...}"
  },
  "filenames": {
    "html": "youtube_roi_report_2026-02-14_10-30-45.html",
    "pdf": "youtube_roi_report_2026-02-14_10-30-45.pdf",
    "text": "youtube_roi_report_2026-02-14_10-30-45.txt",
    "json": "youtube_roi_data_2026-02-14_10-30-45.json"
  },
  "metadata": {
    "generated_at": "2026-02-14T10:30:45",
    "user_id": null,
    "record_count": 47,
    "total_videos": 47,
    "overall_roi": 266.85
  }
}
```

### 3. Download Reports
**GET** `/download/{format}?user_id={optional}`

Download report in specific format.

**Formats:**
- `html` - HTML report file
- `pdf` - PDF report file
- `text` - Plain text report
- `json` - Raw JSON data

**Response:** File download

## Usage

### Backend Testing

Test the YouTube report generator directly:

```bash
cd backend
python -m app.services.youtube_report.youtube_pdf_generator
```

### Frontend Access

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Navigate to: `http://localhost:3000/youtube-report`

### Using the Frontend

1. **Preview Tab**
   - Click "Preview Data" to check available YouTube data
   - View quick statistics (views, revenue, ROI)
   - Verify data before generating full report

2. **Full Report Tab**
   - Click "Generate Report" to create comprehensive analysis
   - View report metrics and preview
   - Download in preferred format (HTML, PDF, Text, JSON)

## Report Features

### AI-Powered Analysis

The system uses Google Gemini 2.0 Flash to analyze:

1. **Executive Summary**
   - Overall channel performance
   - Key financial metrics
   - Strategic positioning

2. **Key Insights**
   - ROI performance analysis
   - Engagement patterns
   - Growth indicators
   - Content effectiveness

3. **Content Strategy**
   - Top performing categories
   - Content recommendations
   - Upload optimization

4. **Growth Opportunities**
   - Audience expansion tactics
   - Content optimization
   - Revenue diversification

5. **Algorithm Optimization**
   - YouTube algorithm tips
   - Engagement strategies
   - Visibility improvements

6. **Future Roadmap**
   - 30/60/90-day action plan
   - Strategic priorities
   - Growth milestones

### Report Formats

1. **HTML**
   - Professional styling
   - Print-optimized layout
   - Interactive in browser

2. **PDF**
   - Portrait orientation
   - Professional formatting
   - Ready for sharing

3. **Text**
   - Plain text extraction
   - Accessible format
   - Email-friendly

4. **JSON**
   - Raw data export
   - API integration
   - Custom processing

## Customization

### Modify AI Analysis

Edit `youtube_ai_agent.py`:

```python
# Change AI model
self.model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # Change model here
    temperature=0.3,  # Adjust creativity
    max_output_tokens=8192  # Adjust response length
)

# Customize analysis prompt
def _create_youtube_analysis_prompt(self, youtube_data):
    # Add custom analysis requirements
    return f"""
    Your custom prompt here...
    """
```

### Customize HTML Template

Edit `_generate_youtube_template_html()` in `youtube_ai_agent.py`:

```python
# Modify colors
.header h1 {
    color: #FF0000;  # YouTube red
}

# Add custom sections
html_content += """
    <div class="custom-section">
        <h3>Custom Analysis</h3>
        <!-- Your content -->
    </div>
"""
```

### Add Custom Metrics

1. Update Firestore data structure
2. Modify `_process_youtube_data()` to include new metrics
3. Update HTML template to display new data

## Troubleshooting

### Common Issues

1. **Firebase Connection Failed**
   - Verify `.env` has correct Firebase credentials
   - Check private key formatting (keep `\n` for newlines)
   - Ensure service account has Firestore read permissions

2. **No Data Found**
   - Check Firestore collection name is `roi_metrics`
   - Verify documents have required fields
   - Use preview endpoint to check data availability

3. **PDF Generation Failed**
   - Install xhtml2pdf: `pip install xhtml2pdf==0.2.13`
   - HTML will still be available if PDF fails
   - Check for complex CSS (xhtml2pdf has limitations)

4. **AI Analysis Not Working**
   - Verify `GOOGLE_API_KEY` in `.env`
   - Check API quota limits
   - System falls back to basic analysis if AI unavailable

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check System Status

```bash
# Test Firestore connection
cd backend
python -c "from app.core.firestore_client import firestore_client; import asyncio; asyncio.run(firestore_client.get_collection_stats('roi_metrics'))"

# Test AI agent
python -m app.services.youtube_report.youtube_ai_agent

# Test full generator
python -m app.services.youtube_report.youtube_pdf_generator
```

## Performance Considerations

- **Large Datasets**: Limit query to last 1000 records by default
- **AI Generation**: Takes 10-30 seconds depending on data size
- **PDF Conversion**: Adds 2-5 seconds to generation time
- **Caching**: Consider implementing report caching for frequently accessed data

## Security

- Firebase service account credentials in `.env` (never commit)
- API keys secured server-side only
- Frontend uses proxy through backend API
- User ID filtering prevents unauthorized access

## Future Enhancements

- [ ] Add date range filtering
- [ ] Compare multiple time periods
- [ ] Export to Excel format
- [ ] Email report scheduling
- [ ] Dashboard with real-time metrics
- [ ] Custom branding options
- [ ] Multi-language support

## Support

For issues or questions:
1. Check this documentation
2. Review backend logs
3. Test individual components
4. Verify Firestore data structure

## License

Part of BOS Solution KitaHack 2026 project.
