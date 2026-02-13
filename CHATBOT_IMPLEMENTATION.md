# Chatbot Implementation Guide

## Overview
This chatbot is powered by Google Gemini AI and provides marketing assistance for SMEs.

## Backend Implementation

### Files Created:
1. **`backend/app/schemas/chat.py`** - Pydantic models for chat requests/responses
2. **`backend/app/services/chat_service.py`** - Core chat service with Gemini integration
3. **`backend/app/api/v1/routers/chat.py`** - FastAPI router for chat endpoints

### API Endpoints:
- **POST `/api/v1/chat/message`** - Send a message and get a complete response
- **POST `/api/v1/chat/stream`** - Stream responses in real-time (SSE)
- **GET `/api/v1/chat/health`** - Check chat service health

### Configuration:
The chatbot uses the `GOOGLE_API_KEY` from your `.env` file and is configured to use the `gemini-2.0-flash-exp` model.

## Frontend Implementation

### Files Created/Modified:
1. **`frontend/lib/api/chat.ts`** - API client for chat communication
2. **`frontend/components/chat/chat-area.tsx`** - Updated to use real API
3. **`frontend/components/chat/chat-input.tsx`** - Added disabled state support

### Features:
- Real-time chat with AI assistant
- Conversation history tracking
- Loading states and error handling
- User authentication integration

## How to Use

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
pip install google-generativeai
```

### 2. Start Backend Server
```bash
cd backend
python main.py
```
The backend will run on `http://localhost:8000`

### 3. Start Frontend
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:3000`

### 4. Test the Chat
1. Sign in to the application
2. Navigate to the chat page
3. Type a message and press Send
4. The AI will respond with marketing insights and assistance

## Model Configuration

The chatbot currently uses `gemini-2.0-flash-exp`. To change the model:

Edit `backend/app/services/chat_service.py`:
```python
self.model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',  # Change this
    system_instruction=self._get_system_instruction()
)
```

Available models:
- `gemini-2.0-flash-exp` - Latest experimental (fastest, most advanced)
- `gemini-1.5-flash` - Stable, fast
- `gemini-1.5-pro` - More capable, slower

## Conversation History

The chatbot maintains conversation context by sending previous messages with each request. This allows for:
- Contextual responses
- Follow-up questions
- Multi-turn conversations

## Error Handling

- Network errors are caught and displayed to users
- API errors return user-friendly messages
- Loading states prevent duplicate submissions

## Future Enhancements

1. **Streaming Responses**: Implement real-time streaming for faster perceived response
2. **Conversation Persistence**: Save conversations to Firebase Firestore
3. **Multi-modal Support**: Add image/file upload capabilities
4. **Advanced Analytics**: Track conversation metrics and user engagement
5. **Custom Prompts**: Allow users to customize AI behavior per conversation

## Troubleshooting

### Backend Issues:
- Ensure `GOOGLE_API_KEY` is set in `.env`
- Check that all dependencies are installed
- Verify the API key is valid

### Frontend Issues:
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_BASE_URL` in `.env.local`

### API Key Issues:
- Get a new key from: https://aistudio.google.com/app/apikey
- Ensure the key has Gemini API access enabled
- Check for rate limits if getting 429 errors
