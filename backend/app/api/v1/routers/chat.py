from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import agent_service  # New LangGraph agent with HITL
from app.services.chat_service import chat_service  # Legacy service (fallback)
import json

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse, summary="Send a chat message")
async def send_message(request: ChatRequest):
    """
    Send a message to the AI assistant and get a response
    Uses LangGraph agent with Human-in-the-Loop (HITL) approval for tool execution
    
    Args:
        request: ChatRequest containing the message and optional conversation history
        
    Returns:
        ChatResponse with the AI's response, optional chart configurations, and optional approval request
    """
    try:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Use LangGraph Agent Service (with native HITL middleware)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Prepare approval decision if provided
        approval_decision = None
        if request.approval_decision:
            approval_decision = {
                "thread_id": request.approval_decision.thread_id,
                "approved": request.approval_decision.approved,
                "tool_name": request.approval_decision.tool_name
            }
        
        # Call agent service
        response_text, charts, requires_approval, approval_request, thread_id = await agent_service.chat(
            user_message=request.message,
            conversation_history=request.conversation_history,
            user_id=request.user_id,
            user_email=request.user_email,
            thread_id=request.thread_id,
            approval_decision=approval_decision
        )
        
        return ChatResponse(
            message=response_text,
            conversation_id=None,
            charts=charts,
            requires_confirmation=False,  # Legacy field
            confirmation_request=None,  # Legacy field
            requires_approval=requires_approval,
            approval_request=approval_request,
            thread_id=thread_id
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.post("/stream", summary="Stream chat responses")
async def stream_message(request: ChatRequest):
    """
    Stream responses from the AI assistant in real-time
    
    Args:
        request: ChatRequest containing the message and optional conversation history
        
    Returns:
        StreamingResponse with chunks of the AI's response
    """
    try:
        async def generate():
            async for chunk in chat_service.chat_stream(
                user_message=request.message,
                conversation_history=request.conversation_history,
                user_id=request.user_id
            ):
                # Send each chunk as a JSON object
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            
            # Send final done signal
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream chat message: {str(e)}"
        )


@router.get("/health", summary="Check chat service health")
async def health_check():
    """Check if the chat service is operational"""
    try:
        # Simple test to see if the service is initialized
        return {
            "status": "healthy",
            "service": "chat",
            "model": "gemini-2.5-flash-lite"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Chat service unavailable: {str(e)}"
        )
