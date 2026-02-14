# BossolutionAI Backend API

AI-Powered Marketing and Advertisement API for SMEs.

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           ├── __init__.py
│   │           └── items.py          # Items API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                 # Environment & settings
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── item.py                   # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── items.py                  # Business logic layer
│   └── __init__.py
├── main.py                           # FastAPI app entry point
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Project metadata
├── .env                              # Environment variables (not in git)
└── README.md                         # This file
```

## Features
- FastAPI application with modular structure (routers, services, schemas)
- CORS configured for frontend integration (Next.js)
- Environment-based settings using Pydantic
- Health check endpoint
- RESTful API with automatic OpenAPI documentation
- Service layer pattern for clean architecture

## Getting Started

### 1. Create a virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the backend root:

```env
# App Settings
PROJECT_NAME="BossolutionAI API"
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000

# Firebase (for Authentication & Firestore)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email

# AI API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 4. Run the development server
```powershell
python main.py
```

Or with uvicorn:
```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access the API

- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc  
- **Health Check:** http://localhost:8000/health

## 📡 API Endpoints

### Health Check
```
GET /health
```

### CopilotKit AGUI Endpoints

#### Supervisor Agent AGUI
```
/api/v1/copilotkit/supervisor     # AGUI streaming endpoint
```
- **Protocol:** AGUI (Agent-UI Interface)
- **Capabilities:**
  - Real-time token streaming
  - Tool call streaming
  - Human-in-the-loop (HITL) interrupts
  - Generative UI events
  - State broadcasting

#### CopilotKit Health Check
```
GET /api/v1/copilotkit/health
```

#### Fallback REST Chat
```
POST /api/v1/copilotkit/supervisor/chat
```

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello, who are you?"}
  ],
  "thread_id": "thread-123",
  "user_id": "user-456"
}
```

**Response:**
```json
{
  "response": "I am BossolutionAI...",
  "thread_id": "thread-123"
}
```

### Multi-Agent Chat API
```
POST   /api/v1/chat             # Multi-agent chat endpoint
```

### Cron Jobs Management
```
GET    /api/v1/crons/           # List all cron jobs
POST   /api/v1/crons/           # Create new cron job
DELETE /api/v1/crons/{id}       # Delete cron job
```

## 🔌 Frontend Integration

The API is configured with CORS to allow requests from:
- `http://localhost:3000` (Next.js default)
- `http://localhost:3001` (Your current frontend)
- `http://localhost:5173` (Vite default)

### CopilotKit Frontend Integration

```typescript
// app/layout.tsx or app/page.tsx
import { CopilotKit } from "@copilotkit/react-core";

export default function RootLayout({ children }) {
  return (
    <CopilotKit 
      runtimeUrl="http://localhost:8000/api/v1/copilotkit/supervisor"
      agent="supervisor_agent"
    >
      {children}
    </CopilotKit>
  );
}
```

### Standard REST API Usage

```typescript
// Fetch data
const response = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    message: 'Monitor Nike',
    thread_id: 'thread-123'
  })
});
const data = await response.json();
```
pytest
```

The interactive API documentation will be available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
