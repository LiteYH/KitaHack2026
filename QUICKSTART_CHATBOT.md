# 🚀 Quick Start - Chatbot Setup

## Prerequisites
- ✅ Python 3.8+ installed
- ✅ Node.js 18+ installed
- ✅ Google API Key configured in `.env`

## Installation & Setup (First Time Only)

### Backend Setup
```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Install Google Generative AI (if not in requirements.txt)
pip install google-generativeai
```

### Frontend Setup
```powershell
# Navigate to frontend
cd frontend

# Install dependencies (if not already done)
npm install
```

## Running the Application

### Option 1: Two Terminals (Recommended)

**Terminal 1 - Backend:**
```powershell
cd backend
python main.py
```
✅ Backend running at: http://localhost:8000

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```
✅ Frontend running at: http://localhost:3000

### Option 2: One Terminal (Background Backend)
```powershell
# Start backend in background
cd backend
Start-Process python -ArgumentList "main.py" -NoNewWindow

# Start frontend
cd ..\frontend
npm run dev
```

## Testing the Chatbot

1. Open browser: http://localhost:3000
2. Sign in with your account
3. Navigate to: http://localhost:3000/chat
4. Type a message like: "Hello! Help me with marketing strategies"
5. Watch the AI respond! 🎉

## Quick Tests

### Test Backend Health
```powershell
# In a new terminal
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/chat/health
```

### Run Unit Tests
```powershell
cd backend
python test_chat.py
```

### Run Integration Tests
```powershell
# Make sure server is running first!
cd backend
python test_integration.py
```

## Common Commands

### Restart Backend
```powershell
# Stop: Ctrl+C in the backend terminal
# Start: 
cd backend
python main.py
```

### Restart Frontend
```powershell
# Stop: Ctrl+C in the frontend terminal
# Start:
cd frontend
npm run dev
```

## API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Backend won't start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F

# Try again
python main.py
```

### Frontend won't start
```powershell
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process if needed
taskkill /PID <process_id> /F

# Or use different port
npm run dev -- -p 3001
```

### "Module not found" errors
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### API Key Issues
1. Check `.env` file in backend folder
2. Verify `GOOGLE_API_KEY` is set correctly
3. Test key at: https://aistudio.google.com

## Development Workflow

```powershell
# Morning routine:
1. cd backend && python main.py         # Terminal 1
2. cd frontend && npm run dev            # Terminal 2
3. Open http://localhost:3000/chat       # Browser
4. Start coding! ✨

# End of day:
1. Ctrl+C in both terminals
2. Git commit your changes
```

## Environment Variables

### Backend (.env)
```env
GOOGLE_API_KEY=your_key_here
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## What's Next?

✅ Chatbot is working!  
✅ Connected to Gemini AI  
✅ Frontend and backend integrated  

**Now you can:**
- Chat with the AI
- Test marketing queries
- Customize the system prompt
- Add more features

## Need Help?

- 📖 Read: `CHATBOT_IMPLEMENTATION.md`
- 📋 Check: `CHATBOT_SUMMARY.md`
- 🔍 Debug: Check browser console (F12)
- 🐛 Issues: Check backend terminal for errors

---

**Happy Coding! 🎉**
