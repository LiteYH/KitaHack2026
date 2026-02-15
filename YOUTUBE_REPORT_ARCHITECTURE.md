# YouTube ROI Report Generator - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  youtube-report/page.tsx                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐   │  │
│  │  │   Preview   │  │    Report   │  │  Download Buttons  │   │  │
│  │  │     Tab     │  │     Tab     │  │  (HTML/PDF/Text)   │   │  │
│  │  └─────────────┘  └─────────────┘  └────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼ HTTP Requests                        │
└────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────┐
│                              ▼                                       │
│                    BACKEND (FastAPI)                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           API Router (youtube_report.py)                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐  │  │
│  │  │  /preview   │  │  /generate  │  │  /download/{fmt}   │  │  │
│  │  └─────────────┘  └─────────────┘  └────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         PDF Generator (youtube_pdf_generator.py)             │  │
│  │                    ┌─────────────┐                           │  │
│  │                    │ Orchestrate │                           │  │
│  │                    │  Workflow   │                           │  │
│  │                    └──────┬──────┘                           │  │
│  └───────────────────────────┼──────────────────────────────────┘  │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          AI Agent (youtube_ai_agent.py)                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐  │  │
│  │  │ Fetch Data  │─▶│  AI Analyze │─▶│ Generate HTML      │  │  │
│  │  └─────────────┘  └─────────────┘  └────────────────────┘  │  │
│  │         │                 │                     │            │  │
│  └─────────┼─────────────────┼─────────────────────┼────────────┘  │
│            │                 │                     │                │
│            ▼                 │                     ▼                │
│  ┌─────────────────┐         │          ┌──────────────────┐      │
│  │ Firestore Client│         │          │  HTML Template   │      │
│  │   (Firebase)    │         │          │   Generator      │      │
│  └─────────────────┘         ▼          └──────────────────┘      │
│            │        ┌──────────────────┐                           │
│            │        │  Google Gemini   │                           │
│            │        │    AI (2.0)      │                           │
│            │        └──────────────────┘                           │
└────────────┼──────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FIREBASE / FIRESTORE                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Collection: roi_metrics                         │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Document 1: { views, likes, revenue, ... }           │  │  │
│  │  │  Document 2: { views, likes, revenue, ... }           │  │  │
│  │  │  Document 3: { views, likes, revenue, ... }           │  │  │
│  │  │  ...                                                   │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌────────┐     1. Request      ┌─────────────┐
│        │─────────────────────▶│             │
│  User  │                      │  Frontend   │
│        │◀─────────────────────│   (React)   │
└────────┘  9. Display Report   └──────┬──────┘
                                       │ 2. API Call
                                       ▼
                                ┌──────────────┐
                                │  API Router  │
                                │   (FastAPI)  │
                                └──────┬───────┘
                                       │ 3. Generate
                                       ▼
                                ┌──────────────┐
                                │     PDF      │
                                │  Generator   │
                                └──────┬───────┘
                                       │ 4. Invoke
                                       ▼
                                ┌──────────────┐
                         ┌─────▶│  AI Agent    │◀──────┐
                         │      └──────┬───────┘       │
                         │             │               │
                5. Fetch │             │ 6. Analyze    │ 7. Generate
                   Data  │             ▼               │    HTML
                         │      ┌──────────────┐       │
                         │      │   Google     │       │
                  ┌──────┴────┐ │   Gemini AI  │ ┌────┴──────┐
                  │ Firestore │ └──────────────┘ │  Template │
                  │  Client   │                  │  Engine   │
                  └──────┬────┘                  └───────────┘
                         │                             │
                         │ 5a. Query                   │
                         ▼                             │
                  ┌──────────────┐                     │
                  │  Firestore   │                     │
                  │   Database   │                     │
                  └──────────────┘                     │
                                                       │
                         ┌─────────────────────────────┘
                         │ 8. Return HTML
                         ▼
                  ┌──────────────┐
                  │  xhtml2pdf   │
                  │  Converter   │
                  └──────┬───────┘
                         │
                         │ 8a. Create PDF
                         ▼
                  ┌──────────────┐
                  │   Multiple   │
                  │   Formats    │
                  │ HTML/PDF/TXT │
                  └──────────────┘
```

## Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
          ┌─────────────────────────────────┐
          │    Click "Preview Data"         │
          │    Click "Generate Report"      │
          │    Click "Download PDF"         │
          └──────────────┬──────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND ACTIONS                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Preview    │  │   Generate   │  │   Download   │     │
│  │   Handler    │  │   Handler    │  │   Handler    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │ GET              │ POST             │ GET         │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   API ENDPOINTS                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  /preview    │  │  /generate   │  │/download/pdf │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         │ Quick Stats      │ Full Flow        │ File Only   │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│               BUSINESS LOGIC LAYER                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          YouTube PDF Generator                      │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  1. Call AI Agent                            │  │   │
│  │  │  2. Receive HTML + Analysis                  │  │   │
│  │  │  3. Convert HTML to PDF (xhtml2pdf)          │  │   │
│  │  │  4. Extract Text (BeautifulSoup)             │  │   │
│  │  │  5. Encode PDF to Base64                     │  │   │
│  │  │  6. Return All Formats                       │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           YouTube AI Agent                          │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  1. Fetch Data (Firestore Client)           │  │   │
│  │  │  2. Process Data (Aggregation)               │  │   │
│  │  │  3. Create AI Prompt                         │  │   │
│  │  │  4. Call Gemini AI (if available)            │  │   │
│  │  │  5. Parse AI Response / Basic Analysis       │  │   │
│  │  │  6. Generate HTML (Template Engine)          │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Firestore Client                           │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  • Initialize Firebase Admin SDK            │  │   │
│  │  │  • Query roi_metrics collection              │  │   │
│  │  │  • Filter by user_id (optional)              │  │   │
│  │  │  • Order by created_at DESC                  │  │   │
│  │  │  • Limit to 1000 records                     │  │   │
│  │  │  • Return document list                      │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                         │
│  ┌──────────────────┐         ┌───────────────────┐        │
│  │    Firestore     │         │   Google Gemini   │        │
│  │    Database      │         │       AI API      │        │
│  │  (roi_metrics)   │         │   (2.0 Flash)     │        │
│  └──────────────────┘         └───────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
KitaHack2026/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── firestore_client.py      ◄── Firebase/Firestore connection
│   │   │   └── config.py                ◄── Environment settings
│   │   │
│   │   ├── services/
│   │   │   └── youtube_report/
│   │   │       ├── __init__.py
│   │   │       ├── youtube_ai_agent.py  ◄── AI analysis & HTML generation
│   │   │       └── youtube_pdf_generator.py  ◄── PDF conversion & orchestration
│   │   │
│   │   └── api/
│   │       └── v1/
│   │           ├── __init__.py
│   │           └── routers/
│   │               └── youtube_report.py  ◄── API endpoints
│   │
│   ├── populate_youtube_data.py  ◄── Sample data generator
│   └── requirements.txt          ◄── Python dependencies
│
├── frontend/
│   └── app/
│       └── youtube-report/
│           └── page.tsx          ◄── React UI component
│
├── YOUTUBE_REPORT.md             ◄── Quick reference
├── YOUTUBE_REPORT_README.md      ◄── Full documentation
├── YOUTUBE_REPORT_QUICKSTART.md  ◄── Setup guide
├── YOUTUBE_REPORT_IMPLEMENTATION.md  ◄── Technical details
├── YOUTUBE_REPORT_ARCHITECTURE.md    ◄── This file
└── test_youtube_report.bat       ◄── Windows test script
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                       │
└─────────────────────────────────────────────────────────────┘

Frontend Layer:
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   Next.js    │    React     │  TypeScript  │  shadcn/ui   │
│    14.x      │    18.x      │    5.x       │  (Tailwind)  │
└──────────────┴──────────────┴──────────────┴──────────────┘

Backend Layer:
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   FastAPI    │  Pydantic    │   Uvicorn    │   Python     │
│    0.119     │    2.12      │    0.37      │    3.10+     │
└──────────────┴──────────────┴──────────────┴──────────────┘

AI & Analysis:
┌──────────────┬──────────────┬──────────────────────────────┐
│   Gemini AI  │  LangChain   │  google-generativeai        │
│  2.0 Flash   │    1.2+      │         0.3+                │
└──────────────┴──────────────┴──────────────────────────────┘

Data & Storage:
┌──────────────┬──────────────┬──────────────────────────────┐
│  Firestore   │ Firebase SDK │  Collection: roi_metrics     │
│   NoSQL DB   │    Admin     │  Documents with YT metrics   │
└──────────────┴──────────────┴──────────────────────────────┘

Report Generation:
┌──────────────┬──────────────┬──────────────────────────────┐
│  xhtml2pdf   │BeautifulSoup │  HTML/CSS Templates          │
│    0.2.13    │    4.12+     │  Portrait orientation        │
└──────────────┴──────────────┴──────────────────────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                        │
└─────────────────────────────────────────────────────────────┘

1. Environment Variables (.env)
   ├── FIREBASE_PROJECT_ID
   ├── FIREBASE_PRIVATE_KEY  ◄── Never committed to git
   ├── FIREBASE_CLIENT_EMAIL
   └── GOOGLE_API_KEY        ◄── Server-side only

2. Firebase Authentication
   ├── Service Account Credentials
   ├── IAM Permissions (Firestore read)
   └── Secure connection (TLS)

3. API Layer Security
   ├── CORS Configuration
   ├── Request Validation (Pydantic)
   ├── Error Handling (no sensitive data leak)
   └── User ID Filtering (optional)

4. Data Access Control
   ├── Collection-level permissions
   ├── User-based filtering
   └── Query limits (max 1000 records)
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOW                      │
└─────────────────────────────────────────────────────────────┘

Frontend ─────▶ API Request
                    │
                    ├─▶ Success ──────▶ Display Report
                    │
                    └─▶ Error
                         │
                         ├─▶ Network Error ──────▶ Show Error Alert
                         ├─▶ 500 Server Error ───▶ Show Error Message
                         └─▶ 404 Not Found ──────▶ Show "No Data"

Backend ──────▶ Process Request
                    │
                    ├─▶ Success ──────▶ Return Data
                    │
                    └─▶ Error
                         │
                         ├─▶ Firestore Error
                         │   ├─▶ Connection Failed ──▶ Return empty data
                         │   └─▶ No Data Found ─────▶ Use sample data
                         │
                         ├─▶ AI Error
                         │   ├─▶ API Key Invalid ───▶ Use basic analysis
                         │   └─▶ Timeout ───────────▶ Fallback analysis
                         │
                         └─▶ PDF Error
                             ├─▶ xhtml2pdf Failed ─▶ Return HTML only
                             └─▶ Template Error ────▶ Use basic template
```

---

**Created:** February 14, 2026  
**Version:** 1.0.0  
**Component:** YouTube ROI Report Generator
